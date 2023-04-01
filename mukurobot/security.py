'''Security module for the bot.
Shoot down the enemy.
After all, the bot’s a sniper, you know.'''

BAD_USERNAME_PATTERNS = (
    'onlyfans.com', 'takaso', 'δøŝ', '是垃', 'csgocases.com', 'freenitro', 'free nitro', '〘𝑅𝑆𝐾〙'
)

def is_bad_user(u, /, *, filename='badusers.txt') -> bool:
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

