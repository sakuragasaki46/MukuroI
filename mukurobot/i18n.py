'''
Ciao, questo è un modulo
Hello, this is a module
Salut, ceci est un module
こんにちは、これはモジュールである

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''


import os
import json
from collections.abc import Mapping
from typing import Optional
from discord import ApplicationContext, Guild

class FileDict(Mapping):
    __slots__ = ('filename', 'data')
    def __init__(self, filename):
        self.filename = filename
        self.data = None
    def load(self):
        self.data = json.load(open(self.filename, 'r'))
    def __getitem__(self, key):
        if self.data is None:
            self.load() 
        return self.data[key]
    def keys(self):
        if self.data is None:
            self.load()
        return self.data.keys()
    def get(self, key, default=None):
        if self.data is None:
            self.load() 
        return self.data.get(key, default)
    def __iter__(self):
        if self.data is None:
            self.load()
        yield from self.data
    def __len__(self):
        if self.data is None:
            self.load()
        return len(self.data)

I18N_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'i18n')

languages = {}

for _l in ('it', 'en'):
    languages[_l] = FileDict(os.path.join(I18N_BASE_DIR, f'{_l}.json'))

def get_language(iso_code):
    lowerize = False
    if iso_code.startswith('_'):
        iso_code = iso_code.lstrip('_')
        lowerize = True

    try:
        lang = languages[iso_code]
    except KeyError:
        lang = languages['en']

    def wrapper(msg):
        m = lang.get(msg, msg)
        if lowerize:
            m = m.lower()
        return m
    return wrapper

def get_language_from_ctx(ctx: Optional[ApplicationContext] = None, *, guild: Guild = None):
    guild = ctx.guild if ctx is not None else guild

    if ctx is None:
        language = 'en'
    elif guild:
        language = ctx.guild.preferred_locale or 'en'

        try:
            # imported here because circular imports
            from .models import GuildConfig
            gc = GuildConfig.from_object(ctx.guild)
            language = gc.language
        except Exception:
            pass
    elif ctx.locale:
        language = ctx.locale
    else:
        language = 'en'

    return get_language(language)


def lang_join(lang, l):
    l = list(filter(None, l))

    comma = lang("and-comma")
    and_ = lang("and")

    if len(l) > 2:
        return and_.join([
            comma.join(l[:-1]),
            l[-1]
        ])
    elif len(l) == 2:
        return and_.join(l)
    elif len(l) == 1:
        return l[0]
    else:
        return lang("nothing")
