'''Functions for the command-line handbook.'''

import os
import re

from .models import Player
from . import __version__ as mukurobot_version

try:
    import readline
except ImportError:
    pass

def parseInt(i):
    return int(re.search('\d+', i).group())

def first_line_doc(c):
    if c.__doc__:
        return c.__doc__.split('\n', 1)[0]
    return c.__name__.capitalize().replace('_', ' ')

def choose_from_options(options=()):
    doc = []
    idx = 1
    for o in options:
        if callable(o):
            doc.append(f'{idx}) {first_line_doc(o)}')
        else:
            doc.append(f'{idx}) {o!s}')
        idx += 1
    doc.append("Choose: ")
    while (i := parseInt(input('\n'.join(doc)))) >= idx or i <= 0:
        print('Invalid option, please try again.')
    chosen = options[i-1]
    return chosen


def view_handbook(uid = None):
    '''View handbook'''
    if uid is None:
        uid = parseInt(input('Enter the user ID to check:'))

    print(f'==== <@{uid}> ====')

    try:
        pl = Player.get(Player.discord_id == uid)
    except Player.DoesNotExist:
        print('Player not found')
        return
    
    print(f'Name: {pl.discord_name}')
    print(f'Pronouns: {pl.pronouns}')
    print(f'Balance: {pl.balance}')
    print(f'Danger Level: {pl.danger_level_str} ({pl.danger_level})')

def view_bulk_handbooks():
    print('Enter now multiple user IDs, terminated by 0.')
    uids = []
    while (uid := parseInt(input())) != 0:
        uids.append(uid)

    for uid in uids:
        view_handbook(uid)


def update_danger_level():
    '''Update danger level'''
    uid = parseInt(input('Enter the user ID to check:'))
    try:
        pl = Player.get(Player.discord_id == uid)
    except Player.DoesNotExist:
        print('Player not found')
        return

    while (level := parseInt(input('Enter danger level [1-5]:'))) < 1 or level > 5:
        print('Invalid level, please try again.')
    
    pl.danger_level = level
    pl.save()

    print(f'{pl.discord_name} danger level set to {pl.danger_level_str}')


def export_badusers_file():
    '''Write badusers.txt'''
    if os.path.exists('badusers.txt') and not input('Confirm overwrite?').lower().startswith('y'):
        print('Operation cancelled.')
        return
    
    with open('badusers.txt', 'w') as f:
        for pl in Player.select().where(Player.danger_level != 0):
            print(f'{pl.discord_id}!{pl.danger_level}', file=f)


def nice_exit():
    '''Exit'''
    raise SystemExit

def handbook():
    '''Main function of the handbook.'''
    try:
        print(f'Mukuro I. {mukurobot_version}')
        print('Command-Line Handbook')
        print('Type an option to get started, or Ctrl-D to exit.')
        while True:
            choose_from_options([
                view_handbook,
                view_bulk_handbooks,
                update_danger_level,
                export_badusers_file,
                nice_exit
            ])()
    except (KeyboardInterrupt, EOFError, SystemExit):
        return

if __name__ == '__main__':
    handbook()