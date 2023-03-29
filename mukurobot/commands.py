
import asyncio
import random
import logging
from discord import Embed, Interaction, User
from discord.app_commands import CommandTree

from .models import Player
from . import CURRENCY_SYMBOL

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
        await inter.response.send_message(f'{pl.discord_name} ha {CURRENCY_SYMBOL} {pl.balance}.')

    @ct.command(name='handbook', description='Apri il tuo e-handbook.')
    async def cmd_handbook(inter: Interaction, u: User = None):
        u = u or inter.user
        pl = Player.from_object(u)

        embed = Embed(
            title=f'E-Handbook di {pl.discord_name}',
            color=0x0033FF
        )
        embed.add_field(name='ID', value=u.id)
        embed.add_field(name='Bilancio', value=u.balance)

        await inter.response.send_message(embed=embed)
    
    return ct

