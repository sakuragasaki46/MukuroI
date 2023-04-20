import asyncio
import dotenv
import os
import argparse
from discord import Intents
import aiohttp
import sys

__version__ = '0.4.0'

dotenv.load_dotenv()

from .client import Mukuro, set_global_client

from .commands import add_commands
from .security import parse_bad_users
from .dbutils import ConnectToDatabase
from .models import database, Player

import logging
logging.basicConfig()

_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)

def main(argv=None):
    from . import timers

    argparser = argparse.ArgumentParser(description='discord bot')
    argparser.add_argument('--sync',  '-s', action='store_true', help='sync commands')
    argparser.add_argument('--enable', '-e', action='store_true', help='enable Message Content intent')
    argparser.add_argument('--check', '-x', action='store_true', help='connectivity check before starting bot')
    argparser.add_argument('--dry-run', '-d', action='store_true', help='do not start the bot')
    argparser.add_argument('--verbose', '-v', action='count', default=0, help='increase verbosity (print incoming messages to stdout etc.)')
    argparser.add_argument('--exclude', '-X', action='append', default=(), help='prevent the named cogs from loading')

    args = argparser.parse_args(argv or sys.argv[1:])

    if args.verbose > 1:
        _log.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        _log.setLevel(logging.INFO)
    else:
        _log.setLevel(logging.WARNING)

    intents = Intents.default()

    # may disappear when the bot reaches 100 guilds
    intents.members = True

    if args.enable:
        intents.message_content = True

    client = Mukuro(
        intents=intents, application_id=os.environ['DISCORD_APPLICATION_ID'],
        auto_sync_commands=args.sync
    )

    set_global_client(client)
    add_commands(client, exclude=args.exclude)

    # update list of dangerous users on each startup

    database.connect()
    count = 0
    for uid, ulevel in parse_bad_users():
        try:
            pl = Player.get(Player.discord_id == uid)
        except Player.DoesNotExist:
            pl = Player.create(
                discord_id = uid,
                discord_name = f'<@{uid}>'
            )
        if pl.danger_level != ulevel:
            pl.danger_level = ulevel
            pl.save()
            count += 1

    _log.info(f'Dangerous users: {count} entries updated')

    if args.check:
        client.plz_check_ip = True
        from .checkip import check_ip, blacklist_from_txt_file
        try:
            asyncio.run(check_ip(blacklist_from_txt_file(os.environ.get('IP_BLACKLIST_FILE', 'ipblacklist.txt'))))
        except aiohttp.ClientConnectionError:
            print('\x1b[31mYou are offline.\x1b[39m')
            return

    if args.dry_run:
        client.is_dry_run = True

    client.run(os.environ['DISCORD_TOKEN'])
