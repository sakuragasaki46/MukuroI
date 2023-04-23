'''
House of the bot class.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

from discord import Bot
import logging

_log : logging.Logger = logging.getLogger(__name__)

from .models import database
from .dbutils import ConnectToDatabase

_client = None

class Mukuro(Bot):
    def __init__(self, *a, **ka):
        super().__init__(*a, **ka)
        self.plz_check_ip = False
        self.is_dry_run = False

    async def on_ready(self):
        _log.info(f'Logged in as \x1b[1m{self.user.name}#{self.user.discriminator}\x1b[22m')

        if self.is_dry_run:
            exit()

        _log.info(f'Started receiving messages…')

    async def on_interaction(self, interaction):
        async with ConnectToDatabase(database):
            await super().on_interaction(interaction)    
                   
def get_client() -> Mukuro | None:
    return _client

def set_global_client(client: Mukuro) -> Mukuro:
    global _client

    if not isinstance(client, Mukuro):
        raise TypeError(f'only instances of {Mukuro.__class__.__name__} allowed!')

    _client = client
    return client


