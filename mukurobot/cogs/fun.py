'''
Trivial commands.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''


import random
from discord import ApplicationContext, slash_command
from discord.ext.commands import Cog

from ..i18n import get_language_from_ctx
from ..models import GuildConfig

class FunCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='rr', description='Roulette russa. Non usare questo comando',
        description_localizations = {
            'en-US': 'Russian Roulette. Don’t use this command',
            'en-GB': 'Russian Roulette. Don’t use this command',
            'it': 'Roulette russa. Non usare questo comando'
        }
    )
    async def cmd_rr(self, inter: ApplicationContext):
        T = get_language_from_ctx(inter)
        if random.randint(1, 6) == 6:
            await inter.response.send_message(T('rr-died'))
            #try:
            #    await asyncio.sleep(10.0)
            #    await inter.user.kick(reason='rr command')
            #except Exception:
            #    _log.error(f'\x1b[31mCould not kick {inter.user.id}\x1b[39m')
        else:
            await inter.response.send_message(T('rr-not-died'))
