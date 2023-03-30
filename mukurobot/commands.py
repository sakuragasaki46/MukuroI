
import asyncio
import random
import logging
from discord import Embed, Interaction, User
from discord.app_commands import CommandTree

from .models import Bibbia, Player
from .utils import money, superscript_number, text_ellipsis

_log : logging.Logger = logging.getLogger(__name__)

def make_ct(client):
    '''Make the command tree.'''
    global ct

    ct = CommandTree(client)

    @ct.command(name='rr', description='Roulette russa. Hai 1/6 di possibilità di essere bannatə /s')
    async def cmd_rr(inter: Interaction):
        if random.randint(1, 6) == 6:
            await inter.response.send_message('Pew! You died.')
            try:
                await asyncio.sleep(10.0)
                await inter.user.kick(reason='rr command')
            except Exception:
                _log.error(f'\x1b[31mCould not kick {inter.user.id}\x1b[39m')
        else:
            await inter.response.send_message('You didn’t die. Lucky!')

    @ct.command(name='bal', description='Il tuo bilancio, o quello di un altro utente.')
    async def cmd_bal(inter: Interaction, u: User = None):
        u = u or inter.user
        pl = Player.from_object(u)
        await inter.response.send_message(f'{pl.discord_name} ha {money(pl.balance)}.')

    @ct.command(name='handbook', description='Apri il tuo e-handbook.')
    async def cmd_handbook(inter: Interaction, u: User = None):
        u = u or inter.user
        pl = Player.from_object(u)

        embed = Embed(
            title=f'E-Handbook di {pl.discord_name}',
            color=0x0033FF
        )
        embed.add_field(name='ID', value=pl.discord_id)
        embed.add_field(name='Bilancio', value=f'{money(pl.balance)}')

        await inter.response.send_message(embed=embed)

    @ct.command(name='bibbia', description='Leggi un versetto della Bibbia')
    async def cmd_bibbia(inter: Interaction, v: str):

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

    @ct.command(name='lore', description='Informazioni (lore) su un determinato soggetto.')
    async def cmd_lore(inter: Interaction, p: str):
        await inter.response.defer()

        from .mwutils import find_page

        page = await find_page(title=p)

        if page:
            await inter.followup.send(
                embed=Embed(
                    title=page.title,
                    url=page.url,
                    description=page.description,
                ).set_footer(text='Informazioni fornite da Città del Dank')
            )
        else:
            await inter.followup.send(
                f'Pagina non trovata: **{p}**'
            )
    
    return ct

