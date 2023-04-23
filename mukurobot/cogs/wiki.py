'''
This cog’s commands pull out some information from wiki sites.

Unfortunately, as of now they do it synchronously… it means they block the entire bot while they are executing.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from discord import ApplicationContext, Cog, Embed, Option, slash_command

from ..mwutils import find_page

class WikiCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name='wiki', description='Informazioni su un determinato soggetto.',
        description_localizations={
            'en-US': 'Info about a certain subject (IT)',
            "en-GB": 'Info about a certain subject (IT)',
            'it': 'Informazioni su un determinato soggetto.'
        },
        options=[
            Option(name='p', description='Il soggetto.'),
            Option(name='source', description='La fonte della lore.',
            choices=['auto', 'wikicord', 'cdd'], required=False)
        ]
    )
    async def cmd_wiki(self, inter: ApplicationContext, p: str, source: str = 'auto'):
        await inter.response.defer()

        source = source or 'auto'
        
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
