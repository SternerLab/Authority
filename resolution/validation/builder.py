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

from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from resolution.parse.parse import remove_stop_words
from .resolver import Resolver
from .utils import chain

class DefaultBuiltResolver(Resolver):
    ''' A specialized class for resolving labels for author clusters '''
    def __init__(self, client, name):
        self.name  = name
        self.cache = None
        self.collection = client.validation[name]
        # Use default resolve(), build_cache(), etc

class Builder:
    def yield_works(self, works):
        raise NotImplementedError

    def yield_search(self, query, key='works', desc='', max_rate=4.0):
        raise NotImplementedError

    def resolve_query(self, resolved_lookup, titles, query): # Order matters for partial *args
        i, query = query
        log.info(f'Thread {i} query: {query}')
        if query not in resolved_lookup: # For efficiency, assuming is definitive
            for source_id, works, n_requests in self.yield_search(query, key='works',
                                                                 desc=f'{query} ({i})',                                                          max_rate=self.thread_max_rate):
                cluster = []
                full    = []
                for title, doi in self.yield_works(works):
                    _id = titles.get(title)
                    if _id is not None:
                        log.info(f'Thread {i} resolved {source_id} = {_id} ({n_requests} requests)')
                        yield title, source_id, _id, doi, n_requests

    def resolve(self, author, titles):
        log.info(f'Resolving by author and JSTOR titles...')
        log.info(f'Author: {author}')
        log.info(f'All titles in JSTOR')
        log.info(f'\n'.join(titles.keys()))

        start = time()

        # First, build a lookup table mapping titles to ids, mongo ids, and DOIs
        resolved_lookup = dict()
        clusters = defaultdict(set)
        if author is None:
            queries = list(titles.keys())
        else:
            queries = [author.name] + list(titles.keys())
        total_requests = 0

        while len(queries) > 0:
            batch = queries[:self.max_threads]; queries = queries[self.max_threads:]
            f = partial(self.resolve_query, resolved_lookup, titles)
            log.info(f'Distributing {self.name} queries across {self.max_threads} threads')
            with ThreadPoolExecutor(max_workers=self.max_threads) as exec:
                pool_result = exec.map(f, enumerate(batch))
            for resolve_gen in pool_result:
                for title, source_id, mongo_id, doi, n_req in resolve_gen:
                    total_requests += n_req
                    clusters[source_id].add(mongo_id)
                    resolved_lookup[title] = (source_id, mongo_id, doi)
                    log.info(f'Resolved {source_id} {mongo_id} {title}')
            log.info(f'Resolved {len(resolved_lookup)} JSTOR articles to entries for {author}')
            duration = (time() - start)
            resolution_rate = len(resolved_lookup) / duration / 60 # minutes
            requests_rate = total_requests / duration # seconds
            log.info(f'Resolution Rate: {resolution_rate} articles per minute')
            log.info(f'Requests Rate: {requests_rate} articles per second')
            if requests_rate >= self.max_rate:
                fix = (total_requests / self.max_rate) - duration + self.buffer
                log.warning(f'Rate exceeded, sleeping {fix}s')
                sleep(fix)
        return resolved_lookup, [list(c) for c in clusters.values()]

    def build(self, client, drop=False, restrict_query=None, query_titles=False,
              query_authors=True):
        if drop:
            client.validation.drop_collection(self.name)
            client.validation.drop_collection(self.name + '_lookup')
        col    = client.validation[self.name]
        lookup = client.validation[self.name + '_lookup']

        filn = client.reference_sets.first_initial_last_name

        titles_cache = build_title_cache(filn)


        names = pd.read_csv('data/names.csv')
        names.sort_values(by='count', ascending=False, inplace=True)
        best_resolutions = dict()
        with client.start_session(causal_consistency=True) as session:
            try:
                for i, a in enumerate(names.itertuples()):
                    if i == 0:
                        continue
                    if restrict_query is not None:
                        if a.key != restrict_query:
                            continue
                    exists = col.find_one({'author.key' : a.key})
                    if exists is not None:
                        log.info(f'The author {a} is already in validation data for {self.name}')
                        continue
                    else:
                        log.info(f'New author {a} being resolved for {self.name}')
                    if query_titles:
                        titles = titles_cache.get(a.key)
                    else:
                        titles = dict()
                    if titles is None:
                        log.warning(f'Found no titles for author {a}')
                        continue
                    if query_authors:
                        author_query = a
                    else:
                        author_query = None
                    resolved_lookup, clusters = self.resolve(author_query, titles)
                    pprint(resolved_lookup)
                    pprint(clusters)
                    col.insert_one(dict(author=dict(key=a.key, full_name=a.name, last=a.last, first_initial=a.first_initial),
                                                     mongo_ids=clusters))
                    lookup.insert_one(dict(key=a.key, lookup=resolved_lookup))
                    print(f'Resolved a total of {len(resolved_lookup)}/{1 + len(titles)} articles for {a.name}')
            except KeyboardInterrupt:
                print(f'Received interrupt, exiting')


def build_title_cache(filn):
    titles_cache = dict()
    for group in track(filn.find(), total=filn.count_documents({}),
                       description='Building title cache'):
        gid    = group['_id']
        key    = f'{gid["first_initial"]}{gid["last"]}'
        titles = dict()
        for doc in group['group']:
            titles[doc['title']] = str(doc['ids'])
        titles_cache[key] = titles
    return titles_cache
