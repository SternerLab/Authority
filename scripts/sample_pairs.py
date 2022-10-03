from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from bson.son import SON
import itertools

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def sample_pairs(group_doc):
    group     = group_doc['group']
    group_id  = group_doc['_id']
    n         = group_doc.get('count', None)
    for pair in itertools.combinations(group, r=2):
        yield dict(group_id=group_id, n=n, pair=list(pair))

def sample_grouped_pairs(database, ref_key):
    total = database[ref_key].count_documents({})
    for group_doc in track(database[ref_key].find(), total=total):
        group_id = group_doc['_id']
        n  = group_doc.get('count', None)
        yield group_id, n, sample_pairs(group_doc)

def run():
    ''' Use the reference sets to create pairs of articles in a new database '''
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    client.drop_database('reference_sets_pairs')
    client.drop_database('reference_sets_group_lookup')
    reference_sets_pairs = client.reference_sets_pairs
    reference_sets_group_lookup = client.reference_sets_group_lookup
    reference_sets = client.reference_sets

    total  = articles.count_documents({})

    ref_keys = ('block', 'match', 'non_match')
    ref_keys = ('non_match',)

    for ref_key in ref_keys:
        print(f'Sampling pairs from {ref_key}', flush=True)
        if ref_key == 'non_match':
            limit = 11295361 # Arbitrary but limited
        else:
            limit = float('inf')
        inserted = 0
        for group_id, n, grouped_pairs in sample_grouped_pairs(reference_sets, ref_key):
            try:
                result = reference_sets_pairs[ref_key].insert_many(grouped_pairs)
                inserted += len(result.inserted_ids)
                reference_sets_group_lookup[ref_key].insert_one(
                        dict(group_id=group_id, pair_ids=result.inserted_ids,
                             n=n))
            except pymongo.errors.InvalidOperation:
                pass # Only one element in group, cannot make pairs
            if inserted > limit:
                break

    for ref_key in ref_keys:
        print(ref_key, reference_sets_pairs[ref_key].count_documents({}))
