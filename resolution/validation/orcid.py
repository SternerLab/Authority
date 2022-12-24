from rich import print
from rich.pretty   import pprint
from rich.progress import track

from functools import partial

import logging
import itertools
import json
from time import time, sleep
from collections import defaultdict

log = logging.getLogger('rich')

import orcid
from concurrent.futures import ThreadPoolExecutor

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
    def __init__(self, creds_path, max_threads=6, max_rate=24., buffer=1.):
        with open(creds_path, 'r') as infile:
            credentials = json.load(infile) # don't save :)
        self.api   = orcid.PublicAPI(credentials['id'], credentials['api_key'])
        self.token = self.api.get_search_token_from_orcid()
        self.max_threads = max_threads
        self.max_rate = max_rate
        self.buffer = buffer

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

    def yield_search(self, query, key='works', desc='', max_rate=3.0):
        start = time()
        n_requests = 1
        results = self.api.search(query, access_token=self.token)
        for result in results['result']:
            orcid_id = result['orcid-identifier']['path']
            try:
                doc = self.api.read_record_public(orcid_id, key, self.token)
                n_requests += 1
                current = time()
                rate = n_requests / (current - start)
                if rate >= max_rate:
                    log.info(f'')
                    sleep(1)
                log.debug(f'OrCID requests/second: {rate}')
            except Exception as e:
                print(f'{type(Exception).__name__}: {e}')
                continue
            yield orcid_id, doc, n_requests

    def resolve_query(self, lookup, titles, query): # Order matters for partial *args
        i, query = query
        log.info(f'Thread {i} query: {query}')
        if query not in lookup: # For efficiency, assuming OrCID is definitive
            for orcid_id, works, n_requests in self.yield_search(query, key='works', desc=f'{query} ({i})'):
                cluster = []
                full    = []
                for title, doi in self.yield_works(works):
                    _id = titles.get(title)
                    if _id is not None:
                        log.info(f'Thread {i} resolved {orcid_id} = {_id} ({n_requests} requests)')
                        yield title, orcid_id, _id, doi, n_requests

    def resolve(self, author, titles):
        log.info(f'Resolving by author and JSTOR titles...')
        log.info(f'Author: {author}')
        log.info(f'All titles in JSTOR')
        log.info(f'\n'.join(titles.keys()))

        start = time()

        # First, build a lookup table mapping titles to OrCID ids, mongo ids, and DOIs
        lookup = dict()
        clusters = defaultdict(set)
        queries = [author.name] + list(titles.keys())
        total_requests = 0

        while len(queries) > 0:
            batch = queries[:self.max_threads]; queries = queries[self.max_threads:]
            f = partial(self.resolve_query, lookup, titles)
            log.info(f'Distributing OrCID queries across {self.max_threads} threads')
            with ThreadPoolExecutor(max_workers=self.max_threads) as exec:
                pool_result = exec.map(f, enumerate(batch))
            for resolve_gen in pool_result:
                for title, orcid_id, mongo_id, doi, n_req in resolve_gen:
                    total_requests += n_req
                    clusters[orcid_id].add(mongo_id)
                    lookup[title] = (orcid_id, mongo_id, doi)
                    log.info(f'Resolved OrCID {orcid_id} {mongo_id} {title}')
            log.info(f'Resolved {len(lookup)} JSTOR articles to OrCID entries for {author.key}')
            duration = (time() - start) / 60 # minutes
            resolution_rate = len(lookup) / duration
            requests_rate = total_requests / duration
            log.info(f'Resolution Rate: {resolve_rate} articles per minute')
            log.info(f'Requests Rate: {requests_rate} articles per minute')
            if requests_rate >= self.max_rate:
                log.warning(f'OrCID rate exceeded, sleeping 1s')
                sleep((l / self.max_rate) - duration + self.buffer)

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
