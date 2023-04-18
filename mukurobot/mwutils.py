'''
XXX Note of the developer: this module is not expected to block while retrieving pages.

However, due to implementation issues and absence of a decent asyncio-compatible
MediaWiki-parsing package, it blocks.
'''

import logging

from mediawiki import MediaWiki
from mediawiki.exceptions import PageError

from collections import namedtuple, OrderedDict

_log = logging.getLogger(__name__)

from .utils import text_ellipsis

mw_cdd = MediaWiki(url='https://cittadeldank.altervista.org/w/api.php')
mw_wc = MediaWiki(url='https://wikicord.miraheze.org/w/api.php')

mws = OrderedDict([
    ('wikicord', mw_wc),
    ('cdd', mw_cdd),
])

mw_site_names = {
    'wikicord': 'Wikicord',
    'cdd': 'Città del Dank'
}

PageObj = namedtuple('Page', 'url title description source_name')

async def find_page(title, source: str = 'auto'):
    if source == 'auto':
        sources = list(mws.keys())
    else:
        sources = [source]
    for s in sources:
        try:
            mw = mws[s]
        except KeyError:
            _log.error(f'Source not recognized: {s!r}')
            continue
    
        try:
            p = mw.page(title)
            return PageObj(p.url, p.title, text_ellipsis(p.content, 4000), mw_site_names[s])
        except PageError:
            _log.info(f'Page not found on {s!r}')
            pass
    else:
        return None