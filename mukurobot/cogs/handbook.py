from discord import ApplicationContext, Embed, Option, User, slash_command, user_command
from discord.ext.commands import Cog

from ..i18n import get_language_from_ctx
from ..dsutils import dm_botmaster
from ..utils import money
from ..models import GuildConfig, Player
from ..inclusion import fetch_pronouns, Pronouns



class HandbookCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # List of users with no danger level set.
        # It resets on every startup, and I’m fine with it
        self.dmd_ids = []
    
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
    async def cmd_handbook(self, inter: ApplicationContext, u: User = None):
        T = get_language_from_ctx(inter)
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
            color=(
                0x990000 if pl.danger_level == 5 else
                0xee5500 if pl.danger_level == 4 else
                0x990099 if pl.danger_level == 3 else
                0x0033ff
            ),
        )
        embed.add_field(name='ID', value=pl.discord_id)
        embed.add_field(name=T('balance'), value=f'{money(pl.balance)}')
        if not u.bot:
            embed.add_field(name=T('danger-level'), value=f'`{pl.danger_level_str}`')

        if u.avatar:
            embed.set_thumbnail(url=u.avatar.url)

        await inter.followup.send(embed=embed)

        if not u.bot and pl.danger_level == 0 and pl.discord_id not in self.dmd_ids:
            await dm_botmaster(
                f'Someone requested information for a user whose danger level is not assessed yet.\n'
                f'Please investigate on this user: {pl.discord_name} <@{pl.discord_id}> ID `{pl.discord_id}`\n'
                f'Once you’re done, please reply with:\n'
                f'`!dan {pl.discord_id}`\n'
                f'followed by the danger level (1-5).'
            )

            self.dmd_ids.append(pl.discord_id)

            if len(self.dmd_ids) > 50:
                self.dmd_ids.pop(0)

    
    cmd_handbook_menu = user_command(
        name='Apri E-Handbook',
        name_localizations={
            'en-US': 'Open E-Handbook',
            'en-GB': 'Open E-Handbook',
            'it': 'Apri E-Handbook',
            'fr': 'Ouvre le manuel électronique'
        }
    )(cmd_handbook)