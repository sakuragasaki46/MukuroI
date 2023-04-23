'''
Inclusion and diversity are important.

Even in destruction.

(c) 2023 Sakuragasaki46
See LICENSE for license information
'''

import aiohttp
import logging

_log = logging.getLogger(__name__)

PRONOUNS_KEYS = {
    'unspecified': '???',
    'hh': 'he/him',
    'hi': 'he/it',
    'hs': 'he/she',
    'ht': 'he/they',
    'ih': 'it/him',
    'ii': 'it/its',
    'is': 'it/she',
    'it': 'it/they',
    'shh': 'she/he',
    'sh': 'she/her',
    'si': 'she/it',
    'st': 'she/they',
    'th': 'they/he',
    'ti': 'they/it',
    'ts': 'they/she',
    'tt': 'they/them',
    'any': 'Any pronouns',
    'other': 'Other pronouns',
    'ask': 'Ask me my pronouns',
    'avoid': 'Avoid pronouns, use my name'
}

class Pronouns(object):
    __slots__ = ('_n', '__weakref__')

    def __new__(cls, ini: str = 'unspecified'):
        obj = super().__new__(cls)
        obj._n = ini
        return obj

    def __str__(self):
        return PRONOUNS_KEYS.get(self._n, self._n)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._n})'

    @property
    def short(self):
        return self._n

    def __bool__(self):
        return self._n not in (None, 'unspecified')


async def fetch_pronouns(discord_id: int):
    async with aiohttp.ClientSession() as client:
        async with client.get(f'https://pronoundb.org/api/v1/lookup?id={discord_id}&platform=discord') as resp:
            if resp.status != 200:
                _log.warn(f'PronounDB: got status {resp.status}')
                return None
            resp_json = await resp.json()
            return Pronouns(resp_json['pronouns'])