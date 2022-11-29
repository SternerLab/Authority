from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from .utils import *
from .resolver import Resolver

possible_heuristics = ['merge', 'split', 'mesh_coauthor', 'middle_initial_suffix']

def merge_heuristic(cluster, client):
    keys = cluster['cluster_labels'].keys()
    labels = {k : 0 for k in keys}
    return labels

def split_heuristic(cluster, client):
    keys = cluster['cluster_labels'].keys()
    labels = {k : i for k, i in zip(keys, range(len(keys)))}
    return labels

class HeuristicResolver(Resolver):
    def __init__(self, client, name):
        self.client = client
        self.name   = name
        match name:
            case 'merge':
                self.heuristic = merge_heuristic
            case 'split':
                self.heuristic = split_heuristic

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
