from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools
from collections import defaultdict

from .features import compare_pair

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs

    for ref_key in pairs.list_collection_names():
        for pair in pairs[ref_key].find():
            pprint(compare_pair(pair, articles))
            1/0
