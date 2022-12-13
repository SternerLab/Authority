from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from authority.parse.parse import parse_citations
from .utils import *
from .resolver import Resolver

def yield_possible_self_citations(article, source_author):
    ''' Return all citations with matching last name and first initial only '''
    # Parse all possible citations, filtering misformatted or old citations
    # for citation in parse_citations(article): # Used if citation parsing is updated
    for citation in article['citations']: # If citation parsing is done already
        # For each citation, check last name and first initial
        # In citations, first names are not reliably included
        for cite_author in citation['authors']:
            if (cite_author['last'] == source_author['last'] and
                cite_author['first_initial'] == source_author['first_initial']):
                yield citation

class SelfCitationResolver(Resolver):
    def yield_clusters(self, entry, articles):
        source_author = entry['authors']
        article   = articles.find_one({'_id' : entry['ids']})
        for citation in yield_possible_self_citations(article, source_author):
            # Once an author is marked as potential self citation, lookup the article
            #   by title, and double-check it is by the same author
            #   in this case, a full first name should be available.
            found = False
            for cite_article in articles.find({'title' : citation['title']}):
                # Check each full author in the resolved article
                for full_cite_author in cite_article['authors']:
                    # Both first and last name should be available after lookup
                    if (full_cite_author['first'] == source_author['first'] and
                        full_cite_author['last'] == source_author['last']):
                        # Note: Do not enable printing unless you are debugging!
                        # This takes 13.7h when printing and 35 minutes without it!
                        # pprint(cite_article)
                        # Sufficient information to do validation by article id
                        yield dict(
                            author=entry['authors'],
                            title=entry['title'],
                            article_id=str(article['_id']),
                            citation=citation,
                            citation_id=str(cite_article['_id']))
                        found = True
                        break
                if found: # To check multiple resolved articles with differing titles
                    break

    def resolve(self, cluster):
        gid = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'
        # print(f'Resolving {key} for {self.name} ')

        article_ids = set(cluster['cluster_labels'].keys())
        resolved = {aid : (i, False) for i, aid in enumerate(article_ids)}

        # Merge clusters based on resolutions
        for cite in self.cache[key]:
            aid, cid = cite['article_id'], cite['citation_id']
            if aid in article_ids and cid is not None and cid in article_ids:
                merge(aid, cid, resolved)

        # # Filter unmerged clusters and decrement cluster labels appropriately
        return make_contiguous({k : v for k, (v, m) in resolved.items() if m})
