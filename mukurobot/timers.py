'''
Tick tack, time passes…

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''


from aiocron import crontab
import datetime
import logging

from discord import User

from .i18n import get_language, lang_join
from .client import get_client
from .models import GuildConfig, Meeting, MeetingGuest
from .dsutils import unlockdown_guild, lockdown_guild

_log = logging.getLogger(__name__)

@crontab('*/15 * * * *')
async def qhourly_task():
    now = datetime.datetime.now()
    tt = int(now.timestamp())
    nowhour = now.hour * 60 + now.minute

    client = get_client()
    if not client:
        return

    _log.debug(f"timer got called at {now=}")

    # daytime start
    for gc in GuildConfig.select().where(GuildConfig.daytime_start == nowhour):
        await unlockdown_guild(gc)

        channel_id = gc.cctv_channel_id or gc.main_channel_id
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f'Sono ora le <t:{tt}:t>. Tempo di alzarsi e splendere!')
                except Exception:
                    _log.warn(f'Could not send to channel #{channel.name}')
            
    # daytime end
    for gc in GuildConfig.select().where(GuildConfig.daytime_end == nowhour):
        channel_id = gc.cctv_channel_id or gc.main_channel_id
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f'Sono ora le <t:{tt}:t>. '
                    'A breve il server sarà bloccato in scrittura. '
                    'Buona notte e sogni d’oro!')
                except Exception:
                    _log.warn(f'Could not send to channel #{channel.name}')

        await lockdown_guild(gc)

    # planned meetings reminder
    for me in Meeting.select().where(
        (Meeting.planned_at >= now + datetime.timedelta(minutes=25)) & 
        (Meeting.planned_at < now + datetime.timedelta(minutes=40))):
        players = me.players()
        notified_users: list[User] = []
        names = [g.guest_name for g in me.guests().where(MeetingGuest.guest_id == None)]
        mt = int(me.planned_at.timestamp())

        for pl in players:
            try:
                notified_users.append(await client.get_or_fetch_user(pl.discord_id))
            except Exception:
                _log.warn(f"Could not fetch user ID {pl.discord_id}")
                names.append(pl.discord_name)
        
        for u in notified_users:
            try:
                mentions = [uu.mention for uu in notified_users if uu != u] 
                names_joined = lang_join(get_language("it"), mentions + names)
                await u.send(
                    f"Hai un incontro dal vivo alle <t:{mt}:t>, <t:{mt}:R> "
                    f"per la seguente ragione: **{me.reason}**\n"
                    f"L’incontro sarà con {names_joined}."
                )
            except Exception as e:
                _log.warn(f"Could not send message to user ID {u.id} (Exception: {e})")

        if me.notify_channel:
            try:
                channel = client.get_channel(me.notify_channel)
                if channel is None:
                    channel = await client.fetch_channel(me.notify_channel)
                if channel is None:
                    _log.warn(f"Could not find channel ID {me.notify_channel}")
                else:
                    mentions = [uu.mention for uu in notified_users][:5]
                    names_joined = lang_join(get_language("it"), mentions + names)

                    await channel.send(
                        f"{names_joined}\n"
                        f"Hai un incontro dal vivo alle <t:{mt}:t>, <t:{mt}:R> "
                        f"per la seguente ragione: **{me.reason}**\n"
                    )
            except Exception as e:
                _log.warn(f"Could not send message to channel ID {me.notify_channel} (Exception: {e})")
        
        _log.debug(f"{me=}")


