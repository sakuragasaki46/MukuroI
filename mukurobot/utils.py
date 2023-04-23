'''
General utilities.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

CURRENCY_SYMBOL = '<:Macoto:1088440100158963733>'

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

