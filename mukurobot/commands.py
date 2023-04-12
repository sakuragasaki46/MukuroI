
import asyncio
import datetime
from pydoc import describe
import random
import logging
from discord import ApplicationContext, AutocompleteContext, Embed, Enum, Interaction, Option, Permissions, User, __version__ as discord_version

from . import __version__ as mukuro_version
from .client import Mukuro, get_client
from .models import Bibbia, GuildConfig, Player, database
from .utils import money, superscript_number, text_ellipsis
from .dsutils import you_do_not_have_permission

_log : logging.Logger = logging.getLogger(__name__)


def add_commands(bot: Mukuro):
    '''Make the command tree.'''

    @bot.command(name='rr', description='Roulette russa. Non usare questo comando',
        description_localizations = {
            'en-US': 'Russian Roulette. Don’t use this command',
            'en-GB': 'Russian Roulette. Don’t use this command',
            'it': 'Roulette russa. Non usare questo comando'
        }
    )
    async def cmd_rr(inter: ApplicationContext):
        gc = GuildConfig.from_object(inter.guild)
        T = gc.get_translate()
        if random.randint(1, 6) == 6:
            await inter.response.send_message(T('rr-died'))
            #try:
            #    await asyncio.sleep(10.0)
            #    await inter.user.kick(reason='rr command')
            #except Exception:
            #    _log.error(f'\x1b[31mCould not kick {inter.user.id}\x1b[39m')
        else:
            await inter.response.send_message(T('rr-not-died'))

    @bot.command(
        name='bal', description='Il tuo bilancio, o quello di un altro utente.',
        description_localizations={
            'en-US': 'Your balance, or the one of another user.',
            'en-GB': 'Your balance, or the one of another user.',
            'it': 'Il tuo bilancio, o quello di un altro utente.'
        },
        options=[
            Option(User, name='u', description='L’utente.', required=False)
        ]
    )
    async def cmd_bal(inter: ApplicationContext, u: User = None):
        u = u or inter.user
        pl = Player.from_object(u)
        await inter.response.send_message(f'{pl.discord_name} ha {money(pl.balance)}.')


    @bot.command(
        name='rich', description='Utenti più ricchi.',
        description_localizations={
            'en-US': 'Richest users.',
            'en-GB': 'Richest users.',
            'it': 'Utenti più ricchi.'
        }
    )
    async def cmd_rich(inter: ApplicationContext):
        gc = GuildConfig.from_object(inter.guild)
        T = gc.get_translate()

        richest = Player.select().order_by(Player.balance.desc()).limit(10)

        await inter.response.send_message(
            embed=Embed(
                title=T('richest'),
                description='\n'.join(
                    f'**#{i+1}** - {u.discord_name} <@{u.discord_id}> ({money(u.balance)})'
                    for i, u in enumerate(richest)
                )
            )
        )

    @bot.command(
        name='handbook', description='Apri il tuo e-handbook.',
        description_localizations={
            'en-US': 'Open your e-handbook.',
            'en-GB': 'Open your e-handbook.',
            'fr': 'Ouvre ton manuel électronique.',
            'it': 'Apri il tuo e-handbook.'
        },
        options=[
            Option(User, name='u', value='L’utente.', required=False)
        ]
    )
    @bot.user_command(
        name='Apri E-Handbook',
        name_localizations={
            'en-US': 'Open E-Handbook',
            'en-GB': 'Open E-Handbook',
            'it': 'Apri E-Handbook',
            'fr': 'Ouvre le manuel électronique'
        }
    )
    async def cmd_handbook(inter: ApplicationContext, u: User = None):
        gc = GuildConfig.from_object(inter.guild)
        T = gc.get_translate()
        u = u or inter.user
        pl = Player.from_object(u)

        embed = Embed(
            title=T('ehandbook-of').format(name=pl.discord_name),
            color=0x0033FF
        )
        embed.add_field(name='ID', value=pl.discord_id)
        embed.add_field(name=T('balance'), value=f'{money(pl.balance)}')

        await inter.response.send_message(embed=embed)

    @bot.command(
        name='bibbia', description='Leggi un versetto della Bibbia',
        description_localizations={
            'en-US': 'Read a verse of the Bible (IT)',
            'en-GB': 'Read a verse of the Bible (IT)',
            'it': 'Leggi un versetto della Bibbia'
        },
        options=[
            Option(name='v', description='Il libro, capitolo e versetto (es. Gn 1:1-12)')
        ]
    )
    async def cmd_bibbia(inter: ApplicationContext, v: str):

        try:
            vv = Bibbia.get_versetti(v)
        except ValueError:
            await inter.response.send_message(
                content = 'Errore! Devi inserire un formato valido es. **Gn 1:1-8**'
            )
        
        content = text_ellipsis(' '.join(
            f'{superscript_number(x.versetto)}{x.testo}'
            for x in vv
        ), 4000)

        await inter.response.send_message(
            embeds = [
                Embed(
                    title = v,
                    description = content
                ).set_footer(text='La Bibbia (edizione CEI 2008)')
            ]
        )

    @bot.command(
        name='lore', description='Informazioni (lore) su un determinato soggetto.',
        description_localizations={
            'en-US': 'Info (lore) about a certain subject (IT)',
            "en-GB": 'Info (lore) about a certain subject (IT)',
            'it': 'Informazioni (lore) su un determinato soggetto.'
        },
        options=[
            Option(name='p', description='Il soggetto.'),
            Option(name='source', description='La fonte della lore.',
            choices=['auto', 'wikicord', 'cdd'], required=False)
        ]
    )
    async def cmd_lore(inter: ApplicationContext, p: str, source: str = 'auto'):
        await inter.response.defer()

        source = source or 'auto'

        from .mwutils import find_page
        
        page = await find_page(title=p, source=source)

        if page:
            await inter.followup.send(
                embed=Embed(
                    title=page.title,
                    url=page.url,
                    description=page.description,
                ).set_footer(text=f'Informazioni fornite da {page.source_name}')
            )
        else:
            await inter.followup.send(
                f'Pagina non trovata: **{p}**'
            )

    # /guildconfig suspended (reason: NO EASY WAY to make subcommands in discord.py) 

    #@ct.group(name='guildconfig', description='Modifica la configurazione del server.')
    #@ct.checks.has_permissions(manage_guild=True)
    #async def cmd_guildconfig(inter: Interaction, k: str, v: str):
    #    pass
    #
    #cmd_guildconfig.default_permissions = Permissions(
    #    manage_guild = True
    #)

    bot_gc = bot.create_group(name='guildconfig', description='Configura le variabili del server.')

    bot_gc.default_member_permissions = Permissions(
        manage_guild=True
    )

    @bot_gc.command(name='view', description='Visualizza le variabili del server.',
        description_localizations={
            'en-US': 'View server variables.',
            'en-GB': 'View guild variables.',
            'it': 'Visualizza le variabili del server.'
        }
    )
    async def cmd_gc_view(inter: ApplicationContext):
        if not inter.user.guild_permissions.manage_guild:
            return await you_do_not_have_permission(inter)

        gc = GuildConfig.from_object(inter.guild)

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
                )
            ),
            ephemeral = True
        )

    async def gc_set_autocomplete(ctx: AutocompleteContext):
        return GuildConfig.get_config_keys(autocomplete=ctx.value)

        
    @bot_gc.command(
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
    async def cmd_gc_set(inter: ApplicationContext, k: str, v: str):
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

    @bot.command(name='stats', description='Statistiche sul bot.',
        description_localizations={
            'en-US': 'Stats about bot.',
            'en-GB': 'Statistics about bot.',
            'it': 'Statistiche sul bot.'
        }
    )
    async def cmd_stats(inter: ApplicationContext):
        await inter.response.send_message(
            f'**Versione Pycord:** {discord_version}\n'
            f'**Versione bot**: {mukuro_version}\n'
            f'**Database**: {database.__class__.__name__}\n'
        )


    @bot.command(
        name='say', description='Parla ufficialmente.',
        description_localizations={
            'en-US': 'Speak officially.',
            'en-GB': 'Speak officially.',
            'it': 'Parla ufficialmente.'
        },
        options=[
            Option(str, name='msg', description='Il tuo messaggio.')
        ]
    )
    async def cmd_say(inter: ApplicationContext, msg: str):
        await inter.response.defer()

        gc = GuildConfig.from_object(inter.guild)

        channel_id = gc.cctv_channel_id or gc.main_channel_id
        if channel_id:
            channel = get_client().get_channel(channel_id)
            if channel:
                try:
                    await channel.send(msg)
                    await inter.response.edit_message(
                        "Messaggio inviato!",
                        ephemeral=True
                    )
                except Exception:
                    _log.warn(f'Could not send to channel #{channel.name}')
                    await inter.response.edit_message(
                        'Messaggio non inviato.',
                        ephemeral=True
                    )
                return
        await inter.response.edit_message(
            'Non hai impostato cctv_channel_id, come pensi di poter dire qualcosa?',
            ephemeral=True
        )
                

    cmd_say.default_member_permissions = Permissions(
        manage_guild=True
    )

    # DO NOT INSERT NEW COMMANDS below this line! 

    return bot


