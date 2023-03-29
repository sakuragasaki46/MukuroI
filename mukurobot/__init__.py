import dotenv
import os
import argparse
from discord import Intents
import requests

__version__ = '0.1.0-dev'

CURRENCY_SYMBOL = '<:Macoto:1088440100158963733>'

dotenv.load_dotenv()

from .client import Mukuro
from .commands import make_ct

def main():
    argparser = argparse.ArgumentParser(description='discord bot')
    argparser.add_argument('--sync',  '-s', action='store_true', help='sync commands')
    argparser.add_argument('--enable', '-e', action='store_true', help='enable Message Content intent')
    argparser.add_argument('--check', '-x', action='store_true', help='connectivity check before starting bot')
    args = None

    args = argparser.parse_args()

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
            check_ip(blacklist_from_txt_file(os.environ.get('IP_BLACKLIST_FILE', 'ipblacklist.txt')), print=True)
        except requests.exceptions.ConnectionError:
            print('\x1b[31mYou are offline.\x1b[39m')

    if args.sync:
        client.plz_do_sync = True

    client.run(os.environ['DISCORD_TOKEN'])
