from discord import Enum
from mediawiki import MediaWiki
from mediawiki.exceptions import PageError

from collections import namedtuple, OrderedDict

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

async def find_page(title, source: str):
    if source == 'auto':
        sources = list(mws)
    else:
        sources = [source]
    for s in sources:
        try:
            mw = mws[s]
        except KeyError:
            return None
    
        try:
            p = mw.page(title)
            return PageObj(p.url, p.title, text_ellipsis(p.content, 4000), mw_site_names[s])
        except PageError:
            pass
    else:
        return None