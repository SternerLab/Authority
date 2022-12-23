from rich import print
from rich.pretty   import pprint
from rich.progress import track

import logging
import itertools
import json
from time import time
from collections import defaultdict

log = logging.getLogger('rich')

import orcid
from resolution.parse.parse import remove_stop_words

from .resolver import Resolver

class OrcidResolver(Resolver):
    ''' A specialized class for resolving labels for author clusters
        To be specifically used for orcid'''
    def __init__(self, client, name):
        self.name  = name
        self.cache = None
        self.collection = client.validation.orcid
        # Use default resolve(), build_cache(), etc

class OrcidScraper:
    def __init__(self, creds_path):
        with open(creds_path, 'r') as infile:
            credentials = json.load(infile) # don't save :)
        self.api   = orcid.PublicAPI(credentials['id'], credentials['api_key'])
        self.token = self.api.get_search_token_from_orcid()

    def yield_works(self, works):
        for work in works['group']:
            summary = work['work-summary']
            for doc in summary:
                try:
                    title = chain(doc, 'title.title.value')
                    title = remove_stop_words(title)
                    doi   = None
                    for ext_id in chain(doc, 'external-ids.external-id'):
                        if ext_id['external-id-type'] == 'doi':
                            doi = ext_id['external-id-value']
                except (KeyError, ValueError, TypeError):
                    pass # DOIs are not critical, so long as we get a few
                yield title, doi

    def yield_search(self, query, key='works', desc=''):
        results = self.api.search(query, access_token=self.token)
        for result in track(results['result'], description=f'OrCID {desc} search'):
            orcid_id = result['orcid-identifier']['path']
            try:
                doc = self.api.read_record_public(orcid_id, key, self.token)
            except Exception as e:
                print(f'{type(Exception).__name__}: {e}')
                continue
            yield orcid_id, doc

    def resolve(self, author, titles):
        log.info(f'Resolving by author and JSTOR titles...')
        log.info(f'Author: {author}')
        log.info(f'All titles in JSTOR')
        log.info(f'\n'.join(titles.keys()))

        start = time()

        all_titles = set()

        # First, build a lookup table mapping titles to OrCID ids, mongo ids, and DOIs
        lookup = dict()
        clusters = defaultdict(set)
        queries = [author.name] + list(titles.keys())
        for i, query in enumerate(queries):
            if i == 0:
                desc = 'author'
            else:
                desc = f'title {i}/{len(titles)}'
            if query not in lookup: # For efficiency, assuming OrCID is definitive
                for orcid_id, works in self.yield_search(query, key='works', desc=desc):
                    cluster = []
                    full    = []
                    for title, doi in self.yield_works(works):
                        all_titles.add(title)
                        _id = titles.get(title)
                        if _id is not None:
                            clusters[orcid_id].add(_id)
                            lookup[title] = (orcid_id, _id, doi)
                            log.info(f'Resolved OrCID {orcid_id} {_id} {title}')
                            log.info(f'Resolved {len(lookup)} JSTOR articles to OrCID entries for {author.key}')
                            duration = (time() - start) / 60 # minutes
                            log.info(f'Rate: {len(lookup) / duration} articles per minute')
        # Then, use the lookup table to build clusters and docs that "just work"
        # with existing validation code
        log.info(f'All titles in OrCID')
        log.info(f'\n'.join(all_titles))
        log.info(f'All titles in JSTOR')
        log.info(f'\n'.join(titles.keys()))
        return lookup, [list(c) for c in clusters.values()]

def chain(data, key, default=None):
    try:
        keys = key.split('.')
        for key in keys:
            data = data[key]
        return data
    except KeyError:
        if default is None:
            raise
        return default

''' API Notes
'group'
'work-summary.title.title.value' : 'MyTitle'
'external-ids.external-id'
'external-id-type' : 'doi'
'external-id-value' : '10.4018...'
'''
