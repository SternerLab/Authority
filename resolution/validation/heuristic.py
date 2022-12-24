from rich.pretty   import pprint
from rich.progress import track
from rich import print
import logging
from collections import defaultdict

import itertools

from .utils import *
from .resolver import Resolver

''' Helper functions '''
log = logging.getLogger('rich')

def _group_id_key(doc):
    return ''.join(x[1] for x in sorted(doc['group_id'].items(), key=lambda t : t[0]))

def _build_lookup_cache(client, ref_key):
    cache = dict()
    lookup   = client.reference_sets_group_lookup[ref_key]
    for doc in track(lookup.find(), total=lookup.count_documents({}), description=f'building {ref_key} cache'):
        key = _group_id_key(doc)
        cache[key] = doc
    return cache

def _lookup_set(client, ref_key, cluster, cache):
    log.info(f'Beginning lookup {ref_key}, {cluster["group_id"]}')
    group_id = cluster['group_id']
    pairs    = client.reference_sets_pairs[ref_key]
    result   = cache.get(_group_id_key(cluster))
    log.info(f'Cached result is {result}')
    if result is None:
        return dict()
    matching_pairs = pairs.find(
            {'_id' : {'$in' : result['pair_ids']}})
    # Str is important here! Won't work otherwise
    id_pairs = ((str(x['ids']) for x in pair['pair']) for pair in matching_pairs)
    labels = pairs_to_cluster_labels(id_pairs)
    log.info(f'Lookup found labels {labels}')
    # pprint(labels)
    return labels

''' Heuristics '''
def mesh_coauthor_heuristic(cluster, client, cache):
    return _lookup_set(client, 'mesh_coauthor_match', cluster, cache)

def name_heuristic(cluster, client, cache):
    return _lookup_set(client, 'name_match', cluster, cache)

def full_name_heuristic(cluster, client, cache):
    labels = _lookup_set(client, 'full_name', cluster, cache)
    log.info('Full name heuristic labels')
    return labels

def merge_heuristic(cluster, client, cache):
    keys = cluster['cluster_labels'].keys()
    labels = {k : 0 for k in keys}
    return labels

def split_heuristic(cluster, client, cache):
    keys = cluster['cluster_labels'].keys()
    labels = {k : i for k, i in zip(keys, range(len(keys)))}
    return labels

# Each heuristic should only have one underscore
possible_heuristics = dict(
    merge=merge_heuristic,
    split=split_heuristic,
    mesh_coauthor=mesh_coauthor_heuristic,
    full_name=full_name_heuristic,
    name=name_heuristic)
# possible_heuristics = {f'{key}_heuristic' : h for key, h in possible_heuristics.items()}

class HeuristicResolver(Resolver):
    def __init__(self, client, name):
        self.client = client
        self.name   = name
        self.heuristic = possible_heuristics[name]
        self.cache = None

    def resolve(self, cluster):
        return self.heuristic(cluster, self.client, self.cache)

    def build_cache(self):
        if self.name == 'name':
            ref_key = 'name_match'
        elif self.name == 'mesh_coauthor':
            ref_key = 'mesh_coauthor_match'
        elif self.name == 'full_name':
            ref_key = 'full_name'
        else:
            return
        self.cache = _build_lookup_cache(self.client, ref_key)
