from mediawiki import MediaWiki
from mediawiki.exceptions import PageError

from collections import namedtuple

from .utils import text_ellipsis

mw = MediaWiki(url='https://cittadeldank.altervista.org/w/api.php')

PageObj = namedtuple('Page', 'url title description')

async def find_page(title):
    try:
        p = mw.page(title)
        return PageObj(p.url, p.title, text_ellipsis(p.content, 4000))
    except PageError:
        return None