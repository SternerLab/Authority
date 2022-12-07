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

def mesh_coauthor_heuristic(cluster, client):
    group_id = cluster['group_id']
    lookup   = client.reference_sets_group_lookup.mesh_coauthor_match
    print(group_id)
    result   = lookup.find_one(dict(group_id=group_id))
    print(result)
    if result is None:
        return dict()
    1/0

def name_heuristic(cluster, client):
    group_id = cluster['group_id']
    lookup   = client.reference_sets_group_lookup.name_match
    print(group_id)
    result   = lookup.find_one(dict(group_id=group_id))
    print(result)
    if result is None:
        return dict()
    1/0

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

    # def yield_clusters(self, entry, articles):
    #     raise NotImplementedError

    # def create(self, client, blocks, articles, query={}, skip=0):
    #     pass
