from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from .utils import *
from .resolver import Resolver

def merge_heuristic(cluster, client):
    keys = cluster['cluster_labels'].keys()
    labels = {k : 0 for k in keys}
    return labels

def split_heuristic(cluster, client):
    keys = cluster['cluster_labels'].keys()
    labels = {k : i for k, i in zip(keys, range(len(keys)))}
    return labels

def _lookup_set(client, reference_set_key, cluster):
    group_id = cluster['group_id']
    lookup   = client.reference_sets_group_lookup[reference_set_key]
    pairs    = client.reference_sets_pairs[reference_set_key]
    result   = lookup.find_one(dict(group_id=group_id))
    if result is None:
        return dict()
    matching_pairs = pairs.find(
            {'_id' : {'$in' : result['pair_ids']}})
    id_pairs = ((x['ids'] for x in pair['pair']) for pair in matching_pairs)
    labels = pairs_to_cluster_labels(id_pairs)
    # pprint(labels)
    return labels

def mesh_coauthor_heuristic(cluster, client):
    return _lookup_set(client, 'mesh_coauthor_match', cluster)

def name_heuristic(cluster, client):
    return _lookup_set(client, 'name_match', cluster)

# Each heuristic should only have one underscore
possible_heuristics = dict(
    merge=merge_heuristic,
    split=split_heuristic,
    meshcoauthor=mesh_coauthor_heuristic,
    name=name_heuristic)
# possible_heuristics = {f'{key}_heuristic' : h for key, h in possible_heuristics.items()}

class HeuristicResolver(Resolver):
    def __init__(self, client, name):
        self.client = client
        self.name   = name
        self.heuristic = possible_heuristics[name]

    def resolve(self, cluster):
        return self.heuristic(cluster, self.client)

    def build_cache(self):
        pass

    # Neither yield_clusters nor create will be used, since the heuristic
    # clusters already exist as "reference sets"
