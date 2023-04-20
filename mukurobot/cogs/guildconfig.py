import datetime
from discord import ApplicationContext, AutocompleteContext, Cog, Embed, Option, Permissions, SlashCommandGroup, slash_command
from discord.abc import GuildChannel

from mukurobot.models import GuildConfig

from ..dsutils import you_do_not_have_permission

import logging

_log = logging.getLogger(__name__)


async def gc_set_autocomplete(ctx: AutocompleteContext):
    return GuildConfig.get_config_keys(autocomplete=ctx.value)



class GuildConfigCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    cmd_gc = SlashCommandGroup(name='guildconfig', description='Configura le variabili del server.')

    cmd_gc.default_member_permissions = Permissions(
        manage_guild=True
    )

    @cmd_gc.command(name='view', description='Visualizza le variabili del server.',
        description_localizations={
            'en-US': 'View server variables.',
            'en-GB': 'View guild variables.',
            'it': 'Visualizza le variabili del server.'
        }
    )
    async def cmd_gc_view(self, inter: ApplicationContext):
        if not inter.user.guild_permissions.manage_guild:
            return await you_do_not_have_permission(inter)

        gc : GuildConfig = GuildConfig.from_object(inter.guild)

        tt = int(datetime.datetime.now().timestamp())
        tt -= tt % 86400

        await inter.response.send_message(
            embed=Embed(
                description=(
                    f'Main Channel: <#{gc.main_channel_id}>\n'
                    f'Main Role: <@&{gc.main_role_id}>\n'
                    f'CCTV Channel: <#{gc.cctv_channel_id}>\n'
                    f'Daytime Start: <t:{tt + gc.daytime_start * 60}:t>\n'
                    f'Daytime End: <t:{tt + gc.daytime_end * 60}:t>\n'
                    f'Language: **{gc.language}**\n'
                    f'Bot Role: <@&{gc.bot_role_id}>\n'
                    f'Risk Checking: **{gc.risk_checking}**\n'
                    f'Traffic Channel: <#{gc.traffic_channel_id}>\n'
                )
            ),
            ephemeral = True
        )

        
    @cmd_gc.command(
        name='set', description='Imposta una variabile del server',
        description_localizations={
            'en-US': 'Set a server variable.',
            'en-GB': 'Set a guild variable.',
            'it': 'Imposta una variabile del server.'
        },
        options=[
            Option(str, name='k', description='Il nome della variabile', autocomplete=gc_set_autocomplete),
            Option(str, name='v', description='Il valore della variabile.')
        ]
    )
    async def cmd_gc_set(self, inter: ApplicationContext, k: str, v: str):
        if not inter.user.guild_permissions.manage_guild:
            return await you_do_not_have_permission(inter)

        gc = GuildConfig.from_object(inter.guild)

        if not(nv := gc.set_config_key(k, v)):
            return await inter.response.send_message(
                f'Chiave non riconosciuta: **{k}**',
                ephemeral=True
            )

        await inter.response.send_message(
            f'Chiave **{k}** impostata a `{nv}`',
            ephemeral=True
        )

    @slash_command(
        name='say', description='Parla ufficialmente.',
        description_localizations={
            'en-US': 'Speak officially.',
            'en-GB': 'Speak officially.',
            'it': 'Parla ufficialmente.'
        },
        options=[
            Option(str, name='msg', description='Il tuo messaggio.'),
            Option(GuildChannel, name='channel', description='Il canale dove mandare il messaggio.', required=False)
        ]
    )
    async def cmd_say(self, inter: ApplicationContext, msg: str, channel: GuildChannel = None):
        await inter.response.defer(ephemeral=True)

        gc = GuildConfig.from_object(inter.guild)

        if not channel:
            channel_id = gc.cctv_channel_id or gc.main_channel_id
            if channel_id:
                channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                await channel.send(msg)
                await inter.followup.send(
                    "Messaggio inviato!",
                    ephemeral=True
                )
            except Exception:
                _log.warn(f'Could not send to channel #{channel.name}')
                await inter.followup.send(
                    'Messaggio non inviato.',
                    ephemeral=True
                )
            return
        await inter.followup.send(
            'Non hai impostato cctv_channel_id, come pensi di poter dire qualcosa?',
            ephemeral=True
        )
                

    cmd_say.default_member_permissions = Permissions(
        manage_guild=True
    )