'''
Money, money, money…

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from discord.ext.commands import Cog
from discord import ApplicationContext, Embed, Option, User, slash_command
from discord.ext.pages import Paginator, Page

from ..i18n import get_language_from_ctx
from ..models import Player
from ..utils import money

class EconomyCog(Cog):
    def __init__(self, bot):
        self.bot = bot


    ## /bal ##
    @slash_command(
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
    async def cmd_bal(self, inter: ApplicationContext, u: User = None):
        T = get_language_from_ctx(inter)
        
        u = u or inter.user
        pl = Player.from_object(u)
        await inter.response.send_message(T('user-has-balance').format(name=pl.discord_name, bal=money(pl.balance)))


    ## /rich ##
    @slash_command(
        name='rich', description='Utenti più ricchi.',
        description_localizations={
            'en-US': 'Richest users.',
            'en-GB': 'Richest users.',
            'it': 'Utenti più ricchi.'
        }
    )
    async def cmd_rich(self, inter: ApplicationContext):
        T = get_language_from_ctx(inter)

        richest = Player.select().where(Player.balance > 0).order_by(Player.balance.desc()).limit(50)

        pages = []

        pidx = 1
        while pidx <= 5 and (p := richest.paginate(pidx, 10)):
            pages.append(Page(
                embeds=[
                    Embed(
                        title=T('richest'),
                        description='\n'.join(
                            f'**#{(pidx-1)*10+i+1}** - {u.discord_name} <@{u.discord_id}> ({money(u.balance)})'
                            for i, u in enumerate(p)
                        )
                    )
                ]
            ))
            pidx += 1

        paginator = Paginator(
            pages=pages
        )

        await paginator.respond(inter.interaction)
    

    