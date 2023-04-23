'''
Monitor incoming and outgoing members.

This is the only part of the bot that requires the GUILD_MEMBERS intent, 
and may disappear if the bot reaches 100 guilds.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from typing import Optional
from discord import Cog, Embed, Member
import logging

from ..utils import money
from ..dsutils import dm_botmaster
from ..i18n import get_language_from_ctx
from ..models import Player, database, GuildConfig
from ..dbutils import ConnectToDatabase

_log = logging.getLogger(__name__)


class TrafficCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener
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
        
    @Cog.listener
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

    @Cog.listener
    async def on_member_ban(self, guild, u):
        async with ConnectToDatabase(database):
            T = get_language_from_ctx(guild=guild)
            
            _log.info(f'Member banned: {u.name}')

            gc = GuildConfig.from_object(guild)
            
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
            
            await main_channel.send(embed=Embed(
                title=T('member-banned'),
                description=T('has-been-banned').format(name=u.name, id=u.id),
                color=0xcc0000
            ))
