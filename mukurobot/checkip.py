import requests

_print = print

def check_ip(blacklist_func=(lambda x:False), /, *, endpoint='https://ipinfo.io/json', print=False):
    resp = requests.get(endpoint)

    if resp.status_code != 200:
        raise RuntimeError(f'API returned status {resp.status_code}')

    ip = resp.json()['ip']

    if print:
        _print(f'IP check requested (your IP: {ip})')

    if blacklist_func(ip):
        raise ValueError(f'IP address disallowed to start connections')

def blacklist_from_txt_file(file):
    def func(ip):
        with open(file, 'r') as f:
            while line := f.readline():
                ipline = line.split('#', 1)[0].strip()
                if ip == ipline:
                    return True
        return False
    return func