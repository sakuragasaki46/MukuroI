'''Security module for the bot.
Shoot down the enemy.
After all, the bot’s a sniper, you know.'''

BAD_USERNAME_PATTERNS = (
    'onlyfans.com', 'takaso', 'δøŝ', '是垃'
)

def is_bad_user(u, /, *, filename='badusers.txt'):
    for upupu in BAD_USERNAME_PATTERNS:
        if upupu in u:
            return True

    uid = str(u.id)

    with open(filename, 'r') as f:
        idline = f.readline().strip()
        if idline == uid:
            return True

    return False

