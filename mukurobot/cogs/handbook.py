from discord import ApplicationContext, Embed, Option, User, slash_command, user_command
from discord.ext.commands import Cog

from ..utils import money
from ..models import GuildConfig, Player
from ..inclusion import fetch_pronouns, Pronouns


class HandbookCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(
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
    @user_command(
        name='Apri E-Handbook',
        name_localizations={
            'en-US': 'Open E-Handbook',
            'en-GB': 'Open E-Handbook',
            'it': 'Apri E-Handbook',
            'fr': 'Ouvre le manuel électronique'
        }
    )
    async def cmd_handbook(self, inter: ApplicationContext, u: User = None):
        gc = GuildConfig.from_object(inter.guild)
        T = gc.get_translate()
        u = u or inter.user
        pl: Player = Player.from_object(u)

        await inter.response.defer()

        if pl.pronouns:
            pronouns = Pronouns(pl.pronouns)
        else:
            pronouns = await fetch_pronouns(pl.discord_id)
            pl.pronouns = pronouns.short
            pl.save()

        embed = Embed(
            title=(
                T('ehandbook-of-pronouns').format(name=pl.discord_name, pronouns=pronouns)
                if pronouns else
                T('ehandbook-of').format(name=pl.discord_name)
            ),
            color=0x0033FF
        )
        embed.add_field(name='ID', value=pl.discord_id)
        embed.add_field(name=T('balance'), value=f'{money(pl.balance)}')
        embed.add_field(name=T('danger-level'), value=f'`{pl.danger_level_str}`')

        await inter.followup.send(embed=embed)