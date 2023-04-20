
from discord import ApplicationContext, Cog, slash_command, __version__ as discord_version
from .. import __version__ as mukuro_version
from ..models import GuildConfig, database, Player


class MetaCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_command(name='stats', description='Statistiche sul bot.',
        description_localizations={
            'en-US': 'Stats about bot.',
            'en-GB': 'Statistics about bot.',
            'it': 'Statistiche sul bot.'
        }
    )
    async def cmd_stats(self, inter: ApplicationContext):
        await inter.response.send_message(
            f'**Versione Pycord:** {discord_version}\n'
            f'**Versione bot**: {mukuro_version}\n'
            f'**Database**: {database.__class__.__name__}\n'
            f'**Utenti**: {Player.select().count()}\n'
            f'**Guilds**: {GuildConfig.select().count()}'
        )