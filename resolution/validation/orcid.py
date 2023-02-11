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
from .builder import *

class OrcidResolver(DefaultBuiltResolver): # Use defaults
    pass

''' OrCID API Notes
'group'
'work-summary.title.title.value' : 'MyTitle'
'external-ids.external-id'
'external-id-type' : 'doi'
'external-id-value' : '10.4018...'
'''
class OrcidBuilder(Builder):
    def __init__(self, creds_path, max_threads=8, max_rate=24., buffer=1.):
        with open(creds_path, 'r') as infile:
            credentials = json.load(infile) # don't save :)
        self.api   = orcid.PublicAPI(credentials['id'], credentials['api_key'])
        self.token = self.api.get_search_token_from_orcid()
        self.max_threads = max_threads
        self.max_rate = max_rate
        self.thread_max_rate = max_rate / max_threads
        self.buffer = buffer
        self.name = 'orcid'

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

    def yield_search(self, query, key='works', desc='', max_rate=4.0):
        start = time()
        n_requests = 1
        results = self.api.search(query, access_token=self.token)
        for result in results['result']:
            orcid_id = result['orcid-identifier']['path']
            try:
                doc = self.api.read_record_public(orcid_id, key, self.token)
                n_requests += 1
                duration = time() - start
                rate = n_requests / duration
                if rate >= max_rate:
                    # log.info(f'Internal thread rate limiting! {rate} >= max_rate')
                    fix = (n_requests / max_rate) - duration + 0.1
                    # log.info(f'Sleeping {fix}s')
                    sleep(fix)
                # log.debug(f'OrCID requests/second: {rate}')
            except Exception as e:
                print(f'{type(Exception).__name__}: {e}')
                continue
            yield orcid_id, doc, n_requests
            n_requests = 0 # Reset


