'''Security module for the bot.
Shoot down the enemy.
After all, the bot’s a sniper, you know.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

import os
import re
import warnings
import logging

_log = logging.getLogger(__name__)

BAD_USERNAME_PATTERNS = (
    'onlyfans.com', 'takaso', 'δøŝ', '是垃', 'csgocases.com', 'freenitro', 'free nitro', '〘𝑅𝑆𝐾〙'
)

ID_ROW_RE = r'^(\d+)(?:\s*!([1-5]))?'

def is_bad_user(u, /, *, filename='badusers.txt') -> bool:
    warnings.warn(f"Use GuildConfig.check_bad_user(player) instead.", DeprecationWarning)

    for くま in BAD_USERNAME_PATTERNS:
        if くま in u.name:
            return True

    uid = str(u.id)

    with open(filename, 'r') as f:
        while line := f.readline():
            idline = line.split('#', 1)[0].strip()
            if not idline:
                continue
            if idline == uid:
                return True

    return False

def parse_bad_users(filename='badusers.txt'):
    if not os.path.exists(filename):
        _log.warn(f'{filename} not found, how are you supposed to detect bad users!?')
        return

    with open(filename, 'r') as f:
        while line := f.readline():
            idline = line.split('#', 1)[0].strip()
            if not idline:
                continue
            if mo := re.match(ID_ROW_RE, idline):
                uid, level = int(mo.group(1)), int(mo.group(2) or 4)
                yield uid, level
