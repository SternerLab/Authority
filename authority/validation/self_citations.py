from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from authority.parse.parse import parse_citations
from .utils import *
from .resolver import Resolver

class SelfCitationResolver(Resolver):
    def yield_clusters(self, entry, articles):
        source_author = entry['authors']
        article   = articles.find_one({'_id' : entry['ids']})
        for citation in parse_citations(article):
            for cite_author in citation['authors']:
                if (cite_author['last'] == source_author['last'] and
                    cite_author['first_initial'] == source_author['first_initial']):
                    cite_article = articles.find_one({'title' : citation['title']})
                    print('resolved self-citation:', source_author, flush=True)
                    yield dict(
                        author=entry['authors'],
                        title=entry['title'],
                        article_id=str(article['_id']),
                        citation=citation,
                        citation_id=(str(cite_article['_id'])
                                     if cite_article is not None else None))
