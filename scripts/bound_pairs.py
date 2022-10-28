from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools
import math

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets = client.reference_sets

    for ref_key in reference_sets.list_collection_names():
        print(ref_key)
        count = 0
        for group in reference_sets[ref_key].find():
            count += math.comb(len(group['group']), 2)
        print(count)
