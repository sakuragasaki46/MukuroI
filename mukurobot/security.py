'''Security module for the bot.
Shoot down the enemy.
After all, the bot’s a sniper, you know.'''

BAD_USERNAME_PATTERNS = (
    'onlyfans.com', 'takaso', 'δøŝ', '是垃'
)

def is_bad_user(u, /, *, filename='badusers.txt') -> bool:
    for upupu in BAD_USERNAME_PATTERNS:
        if upupu in u.name:
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

