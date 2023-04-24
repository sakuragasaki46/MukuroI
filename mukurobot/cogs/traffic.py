'''
Monitor incoming and outgoing members.

This is the only part of the bot that requires the GUILD_MEMBERS intent, 
and may disappear if the bot reaches 100 guilds.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from typing import Optional
from discord import ApplicationContext, ButtonStyle, Cog, Embed, Guild, Interaction, Member, Option, Permissions, User
from discord.ext.commands import slash_command
from discord.ui import View, button
import logging

from ..utils import money
from ..dsutils import dm_botmaster, you_do_not_have_permission
from ..i18n import get_language_from_ctx
from ..models import Player, database, GuildConfig
from ..dbutils import ConnectToDatabase

_log = logging.getLogger(__name__)


async def ban_user(inter: Interaction, guild: Guild, u: User, reason: Optional[str] = None, dm: bool = False):
    if dm and isinstance(u, Member):
        try:
            await u.send(
                f"Sei statə bannatə da **{inter.guild.name}**.\n" + 
                (f"Il moderatore che ha eseguito il ban ha specificato la seguente ragione:\n"
                f"{reason}" if reason else "")
            )
        except Exception:
            dm = False

    try:
        await guild.ban(
            u,
            delete_message_days=0,
            reason=f"Banned by {inter.author.name}#{inter.author.discriminator}: {reason}"
        )
        await inter.response.send_message(
            "Membro bannato." +
            ("L’utente è stato notificato." if dm else ""),
        )
    except Exception:
        await inter.response.send_message(
            "Impossibile bannare il membro.",
            ephemeral=True
        )

class BanView(View):
    def __init__(self, guild: Guild, user: User, reason: Optional[str] = None, dm: bool = False):
        super().__init__(timeout=30.0, disable_on_timeout=True)
        self.user = user
        self.reason = reason
        self.dm = dm
        self.guild = guild
    
    @button(label="Ban", row=0, style=ButtonStyle.danger)
    async def button_callback(self, button, interaction):
        if interaction.author == self.user:
            await interaction.response.send_message(
                'Stai cercando di bannarti da solə, sei davvero così stupidə?',
                ephemeral=True
            )
            return

        if not interaction.author.guild_permissions.ban_members:
            return await you_do_not_have_permission(interaction)

        await self.user.ban(interaction, self.guild, self.user, reason=self.reason, dm=self.dm)


class TrafficCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name='ban', description='Banna un utente',
        description_localizations={
            'en-US': 'Ban a user',
            'en-GB': 'Ban a user',
            'it': 'Banna un utente'
        },
        options = [
            Option(User, name="u", description="L’utente"),
            Option(str, name="reason", description="La ragione del ban.", required=False),
            Option(bool, name="dm", description="Notifica il membro bannato.", required=False)
        ],
        dm_permission=False
    )
    async def cmd_ban(self, inter: ApplicationContext, u: User, reason: Optional[str] = None, dm: bool = False):
        if inter.author == u:
            await inter.response.send_message(
                'Stai cercando di bannarti da solə, sei davvero così stupidə?',
                ephemeral=True
            )
            return

        if not inter.author.guild_permissions.ban_members:
            return await you_do_not_have_permission(inter)

        pl = Player.from_object(u)

        if pl.danger_level < 4:
            await inter.response.send_message(
                f"Bannare {u.name}#{u.discriminator}?",
                view=BanView(inter.guild, u, reason=reason, dm=dm),
                ephemeral=True
            )
        else:
            await ban_user(inter, inter.guild, u, reason=reason, dm=dm)

    cmd_ban.default_member_permissions = Permissions(
        ban_members=True
    )

    @Cog.listener()
    async def on_member_join(self, member: Member):
        ## WARNING This requires a Privileged Intent.
        ## When this bot reaches 100 servers, this event handler’s code
        ## may vanish.
        async with ConnectToDatabase(database):
            gc = GuildConfig.from_object(member.guild)

            _log.info(f'Member joined: {member.name}')

            pl : Optional[Player] = None
            if not member.bot:
                pl = Player.from_object(member)

            if gc.traffic_channel_id:
                traffic_channel = member.guild.get_channel(gc.traffic_channel_id)
                
                if traffic_channel:
                    try:
                        if member.bot:
                            await traffic_channel.send(
                                f'**Bot joined:** `{member.name}#{member.discriminator}` (ID {member.id})\n'
                                f'**Created:** <t:{int(member.created_at.timestamp())}:R>\n'
                                f'**Verified:** {member.public_flags.verified_bot}'
                            )
                        else:
                            await traffic_channel.send(
                                f'**Member joined:** `{member.name}#{member.discriminator}` (ID {member.id})\n'
                                f'**Created:** <t:{int(member.created_at.timestamp())}:R>\n'
                                f'**Danger level:** `{pl.danger_level_str}`'
                            )
                    except Exception:
                        _log.warn(f'Could not send to channel {traffic_channel.id}')
                else:
                    _log.warn(f'Traffic channel not in cache for guild {member.guild.id}')

            first_time = False
            
            if member.bot:
                bot_role = member.guild.get_role(gc.bot_role_id)

                if bot_role:
                    await member.add_role(bot_role)
            elif gc.check_bad_user(pl):
                try:
                    await member.send(
                        f'Sei statə bannatə automaticamente da {member.guild.name} '
                        f'in quanto riconosciuto come malintenzionato/membro AOS.'
                    )
                except Exception:
                    _log.warn(f'Could not DM {member.guild.name}.')

                try:
                    await member.guild.ban(member, reason='Bad actor/AOS member detected')
                    _log.info(f'Banned {member.name} ({member.id})')
                except Exception:
                    _log.error(f'\x1b[31mCould not ban {member.name} ({member.id})\x1b[39m')
            else:
                if not pl.daily_streak_update:
                    first_time = True
                ds_inc = pl.update_daily_streak()
                
                if gc.main_channel_id:
                    main_channel = member.guild.get_channel(gc.main_channel_id)
                else:
                    _log.warn('Main channel not set. Checking if there is a system channel…')
                    # retrieve main channel
                    main_channel = member.guild.system_channel
                    if main_channel:
                        gc.main_channel_id = main_channel.id
                        gc.save()
                    else:
                        _log.warn('No system channel found.')
                
                if pl.danger_level == 0:
                    await dm_botmaster(
                        f'A user whose danger level is not assessed yet joined the guild **{member.guild.name}**.\n'
                        f'Please investigate on this user: {pl.discord_name} <@{pl.discord_id}> ID `{pl.discord_id}`\n'
                        f'Once you’re done, please reply with:\n'
                        f'`!dan {pl.discord_id}`\n'
                        f'followed by the danger level (1-5).'
                    )

                if first_time and main_channel is not None:
                    await main_channel.send(embed=Embed(
                        title='Benvenutə!',
                        description=f'{pl.discord_name}, sembra che sia la prima volta qui.\n' +
                        f'Hai ricevuto {money(ds_inc)} come bonus 🥳'
                    ))
        
    @Cog.listener()
    async def on_member_remove(self, member: Member):
        ## WARNING This requires a Privileged Intent.
        ## When this bot reaches 100 servers, this event handler’s code
        ## may vanish.
        async with ConnectToDatabase(database):
            gc = GuildConfig.from_object(member.guild)

            _log.info(f'Member left: {member.name}')

            pl : Optional[Player] = None
            if not member.bot:
                pl = Player.from_object(member)

            if gc.traffic_channel_id:
                traffic_channel = member.guild.get_channel(gc.traffic_channel_id)
                
                if traffic_channel:
                    try:
                        if member.bot:
                            await traffic_channel.send(
                                f'**Bot left:** `{member.name}#{member.discriminator}` (ID {member.id})\n'
                                f'**Created:** <t:{int(member.created_at.timestamp())}:R>\n'
                                f'**Verified:** {member.public_flags.verified_bot}'
                            )
                        else:
                            await traffic_channel.send(
                                f'**Member left:** `{member.name}#{member.discriminator}` (ID {member.id})\n'
                                f'**Created:** <t:{int(member.created_at.timestamp())}:R>\n'
                                f'**Danger level:** `{pl.danger_level_str}`'
                            )
                    except Exception:
                        _log.warn(f'Could not send to channel {traffic_channel.id}')
                else:
                    _log.warn(f'Traffic channel not in cache for guild {member.guild.id}')

    @Cog.listener()
    async def on_member_ban(self, guild, u):
        async with ConnectToDatabase(database):
            T = get_language_from_ctx(guild=guild)
            
            _log.info(f'Member banned: {u.name}')

            gc = GuildConfig.from_object(guild)
            pl = Player.from_object(u)

            main_channel = None
            if gc.main_channel_id:
                main_channel = guild.get_channel(gc.main_channel_id)
            else:
                _log.warn('Main channel not set. Checking if there is a system channel…')
                # retrieve main channel
                main_channel = guild.system_channel
                if main_channel:
                    gc.main_channel_id = main_channel.id
                    gc.save()
                else:
                    _log.warn('No system channel found.')
            
            if main_channel:
                await main_channel.send(embed=Embed(
                    title=T('member-banned'),
                    description='\n'.join(
                        T('has-been-banned').format(name=u.name, id=u.id),
                        T('banned-n-times').format(n=pl.ban_count)
                    ),
                    color=0xcc0000
                ))
            
            pl.ban_count += 1
            pl.save()