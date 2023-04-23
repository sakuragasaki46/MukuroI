'''
Leveling. Fun.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from discord import Cog, Message

from ..dbutils import ConnectToDatabase
from ..models import Player, database

class LevelsCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener
    async def on_message(self, message: Message):
        if message.guild and not message.author.bot:
            async with ConnectToDatabase(database):
                pl = Player.from_object(message.author)
                pl.update_daily_streak()
        