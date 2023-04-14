from types import FunctionType
import aiohttp
import logging

_log : logging.Logger = logging.getLogger(__name__)
_log.setLevel(logging.INFO)

async def check_ip(blacklist_func=(lambda x:False), /, *, endpoint='https://ipinfo.io/json') -> None:
    async with aiohttp.ClientSession() as client:
        resp = await client.get(endpoint)

        if resp.status != 200:
            raise RuntimeError(f'API returned status {resp.status_code}')

        ip = (await resp.json())['ip']

        _log.info(f'IP check requested (your IP: {ip})')

        if blacklist_func(ip):
            _log.error(f'IP address disallowed to start connections')
            raise ValueError(f'IP address disallowed to start connections')

def blacklist_from_txt_file(file):
    def func(ip) -> bool:
        with open(file, 'r') as f:
            while line := f.readline():
                ipline = line.split('#', 1)[0].strip()
                if ip == ipline:
                    return True
        return False
    return func