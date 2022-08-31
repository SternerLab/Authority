from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def sample_pairs(collection, max_samples=float('inf')):
    count = 0
    cursor = collection.find()
    try:
        while count < max_samples:
            for pair in itertools.combinations(next(cursor)['group'], r=2):
                yield pair
                count += 1
    except StopIteration:
        pass

def run():
    ''' Use the reference sets to create pairs of articles in a new database '''
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    client.drop_database('reference_sets_pairs')
    reference_sets_pairs = client.reference_sets_pairs
    reference_sets = client.reference_sets

    for ref_key in reference_sets.list_collection_names():
        reference_sets_pairs[ref_key].insert_many(
            dict(pair=list(pair)) for pair in sample_pairs(reference_sets[ref_key]))
