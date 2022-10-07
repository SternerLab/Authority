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

# Issue:
# feature_groups_a:
#     match
# feature_groups_i:
#     match_x1
#     match_x2
#     match_x10
#     match_x7
# features:
#     match
# jstor_database

def patch_features(ref_key, client, limit=None):

    jstor_database   = client.jstor_database
    articles         = jstor_database.articles
    pairs            = client.reference_sets_pairs
    features         = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    # for db in (features, feature_groups_a, feature_groups_i):
    #     for coll in db.list_collection_names():
    #         if 'match' in coll:
    #             db[coll].rename(coll.replace())

def run():
    ''' Rename feature groups to match features, not their indexes '''
    client = MongoClient('localhost', 27017)

    for ref_key in client.reference_sets_pairs.list_collection_names():
        if 'match' in ref_key:
            patch_features(ref_key, client=client)

    print(match_group.count_documents({}))
