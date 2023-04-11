from aiocron import crontab
import datetime
import logging

from . import get_client
from .models import GuildConfig
from .dsutils import unlockdown_guild, lockdown_guild

_log = logging.getLogger(__name__)

@crontab('*/15 * * * *')
async def qhourly_task():
    now = datetime.datetime.now()
    nowhour = now.hour * 60 + now.minute

    client = get_client()
    if not client:
        return

    # daytime start
    for gc in GuildConfig.select().where(GuildConfig.daytime_start == nowhour):
        await unlockdown_guild(gc)

        channel_id = gc.cctv_channel_id or gc.main_channel_id
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f'Sono ora le {nowhour // 60:02}:{nowhour % 60:02}. Tempo di alzarsi e splendere!')
                except Exception:
                    _log.warn(f'Could not send to channel #{channel.name}')
            
    # daytime end
    for gc in GuildConfig.select().where(GuildConfig.daytime_end == nowhour):
        channel_id = gc.cctv_channel_id or gc.main_channel_id
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f'Sono ora le {nowhour // 60:02}:{nowhour % 60:02}. '
                    'A breve il server sarà bloccato in scrittura. '
                    'Buona notte e sogni d’oro!')
                except Exception:
                    _log.warn(f'Could not send to channel #{channel.name}')

        await lockdown_guild(gc)
