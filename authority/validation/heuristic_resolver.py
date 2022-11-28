from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from .utils import *
from .resolver import Resolver

class HeuristicResolver(Resolver):
    def __init__(self, client, name):
        pass

    def resolve(self, cluster):
        pass

    # Neither yield_clusters nor create will be used, since the heuristic
    # clusters already exist as "reference sets"

    # def yield_clusters(self, entry, articles):
    #     raise NotImplementedError

    # def create(self, client, blocks, articles, query={}, skip=0):
    #     pass

    # def build_cache(self):
    #     pass
