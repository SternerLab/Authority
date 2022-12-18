from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from .utils import *
from .resolver import Resolver

class ManualResolver(Resolver):
    def __init__(self, client, name):
        raise NotImplementedError

    def resolve(self, cluster):
        raise NotImplementedError

    def build_cache(self):
        raise NotImplementedError

