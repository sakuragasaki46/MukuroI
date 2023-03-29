

CURRENCY_SYMBOL = '<:Macoto:1088440100158963733>'

def money(x, /, *, currency_symbol=CURRENCY_SYMBOL):
    return f'{CURRENCY_SYMBOL} {x:,}'