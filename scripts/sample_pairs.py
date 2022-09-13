from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import Progress, BarColumn, TextColumn
from rich import print
from bson.son import SON
import itertools

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def sample_pairs(collection, max_samples=float('inf')):
    with Progress(BarColumn(), TextColumn('{task.completed}')) as progress:
        task = progress.add_task('',
            total=(max_samples if isinstance(max_samples, int) else None))
        count = 0
        cursor = collection.find()
        try:
            while count < max_samples:
                group = next(cursor)['group']
                for pair in itertools.combinations(group, r=2):
                    yield pair
                    progress.update(task, advance=1)
                    count += 1
                    if count == max_samples:
                        break
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

    total  = articles.count_documents({})
    factor = 2 # an arbitrary factor

    for ref_key in reference_sets.list_collection_names():
        print(f'Sampling pairs from {ref_key}')
        reference_sets_pairs[ref_key].insert_many(
            dict(pair=list(pair))
            for pair in sample_pairs(reference_sets[ref_key],
                max_samples=total * factor))

    for ref_key in reference_sets.list_collection_names():
        print(ref_key, reference_sets_pairs[ref_key].count_documents({}), 'pairs')
