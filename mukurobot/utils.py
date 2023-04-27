'''
General utilities.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

import re
import datetime

CURRENCY_SYMBOL = '<:Macoto:1088440100158963733>'

DATE_RES = [
    r'(?P<d>0?[1-9]|[12][0-9]|3[01])[/.-](?P<m>0?[1-9]|1[0-2])(?:[/.-](?P<c>\d{2})?(?P<y>\d{2}))?[ TH](?P<h>[0-1][0-9]|2[0-3])[:.](?P<i>00|15|30|45)(?:(?P<z>[+-](?:[0-1]?[0-9]|2[0-3]))(?P<zi>00|15|30|45)?)?',
]

def parseInt(i):
    return int(re.search('\d+', i).group())

def money(x, /, *, currency_symbol=CURRENCY_SYMBOL):
    return f'{CURRENCY_SYMBOL} {x:,}'

def letter_range(l, l2):
    for i in range(ord(l), ord(l2)+1):
        yield chr(i)

def superscript_number(n):
    return str(n).translate({
        48: 8304, 49: 185, 50: 178, 51: 179, 52: 8308,
        53: 8309, 54: 8310, 55: 8311, 56: 8312, 57: 8313
    })

def text_ellipsis(text: str, length: int):
    if len(text) < length:
        return text
    else:
        return text[:length-1] + '…'

def parse_date_and_hour(s, *, now=None):
    now = now or datetime.datetime.now()

    for rx in DATE_RES:
        if mg := re.match(rx, s):
            return datetime.datetime(
                100 * int(mg.group('c') or now.year // 100) + int(mg.group('y') or now.year % 100),
                int(mg.group('m')),
                int(mg.group('d')),
                int(mg.group('h')),
                int(mg.group('i')),
                tzinfo=datetime.timezone(datetime.timedelta(
                    hours=int(mg.group('z') or 0),
                    minutes=int(mg.group('zi') or 0)
                )) if mg.group('z') else None
            )
    raise ValueError

