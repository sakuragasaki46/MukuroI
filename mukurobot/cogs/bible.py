from discord import ApplicationContext, Cog, Embed, Option, slash_command

from ..utils import superscript_number, text_ellipsis
from ..models import Bibbia

class BibleCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
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
    async def cmd_bibbia(self, inter: ApplicationContext, v: str):

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