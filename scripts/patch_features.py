from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track, Progress
from bson.son import SON
import itertools
from collections import defaultdict
from functools import partial
from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock

from .features import *

def patch_features(ref_key, client, limit=None):

    jstor_database   = client.jstor_database
    articles         = jstor_database.articles
    pairs            = client.reference_sets_pairs
    features         = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    to_update = []
    for i, j in enumerate(x_i): # Fixed!
        # i is the original index
        # j is the new index, corresponding to the actual feature
        old  = f'{ref_key}_x{i}'
        temp = f'{ref_key}_x{i}.bak'
        new  = f'{ref_key}_x{j}'
        print(f'Renaming {old} to {temp}', flush=True)
        to_update.append((temp, new))
        feature_groups_i[old].rename(temp)
    for temp, new in to_update:
        print(f'Renaming {temp} to {new}', flush=True)
        feature_groups_i[temp].rename(new)

def run():
    ''' Rename feature groups to match features, not their indexes '''
    client = MongoClient('localhost', 27017)

    for ref_key in client.reference_sets_pairs.list_collection_names():
        if 'match' in ref_key:
            patch_features(ref_key, client=client)
