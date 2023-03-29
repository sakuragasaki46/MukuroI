import dotenv
import os
import argparse
from discord import Intents
import requests
import sys

__version__ = '0.2.0-dev'

dotenv.load_dotenv()

from .client import Mukuro
from .commands import make_ct

def main(argv=None):
    argparser = argparse.ArgumentParser(description='discord bot')
    argparser.add_argument('--sync',  '-s', action='store_true', help='sync commands')
    argparser.add_argument('--enable', '-e', action='store_true', help='enable Message Content intent')
    argparser.add_argument('--check', '-x', action='store_true', help='connectivity check before starting bot')
    argparser.add_argument('--dry-run', '-d', action='store_true', help='do not start the bot')
    #argparser.add_argument('--verbose', '-v', action='count', help='increase verbosity (print incoming messages to stdout etc.)')

    args = argparser.parse_args(argv or sys.argv[1:])

    intents = Intents.default()
    intents.members = True

    if args.enable:
        intents.message_content = True

    client = Mukuro(intents=intents, application_id=os.environ['DISCORD_APPLICATION_ID'])

    ct = make_ct(client)

    if args.check:
        client.plz_check_ip = True
        from .checkip import check_ip, blacklist_from_txt_file
        try:
            check_ip(blacklist_from_txt_file(os.environ.get('IP_BLACKLIST_FILE', 'ipblacklist.txt')))
        except requests.exceptions.ConnectionError:
            print('\x1b[31mYou are offline.\x1b[39m')

    if args.sync:
        client.plz_do_sync = True

    if args.dry_run:
        client.is_dry_run = True

    client.run(os.environ['DISCORD_TOKEN'])
