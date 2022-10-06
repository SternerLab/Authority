from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track, Progress
from rich import print
from bson.son import SON
from functools import partial
import itertools
from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock
progress_lock = Lock()

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def sample_pairs(group_doc):
    group     = group_doc['group']
    group_id  = group_doc['_id']
    n         = group_doc.get('count', None)
    accepted  = 0
    rejected  = 0
    for pair in itertools.combinations(group, r=2):
        mesh_a, mesh_b = (p['mesh'] for p in pair)
        if isinstance(mesh_a, list) and isinstance(mesh_b, list):
            accepted += 1
        else:
            rejected += 1
        print(f'Sampling rejected {rejected:6} accepted {accepted:6}')
        # TODO Rejection based on MeSH terms is intentionally ignored for now
        yield dict(group_id=group_id, n=n, pair=list(pair))

def sample_grouped_pairs(database, ref_key):
    total = database[ref_key].count_documents({})
    for group_doc in database[ref_key].find():
        group_id = group_doc['_id']
        n  = group_doc.get('count', None)
        yield group_id, n, sample_pairs(group_doc)

def sample_for_ref_key(ref_key, progress, reference_sets, reference_sets_group_lookup,
                       reference_sets_pairs, every=10000):
    if ref_key == 'differing_last_name':
        limit = 11295361 # Arbitrary but limited
    else:
        limit = float('inf')

    task_name = f'Sampling pairs from {ref_key}'
    total = reference_sets[ref_key].count_documents({})
    with progress_lock:
        task  = progress.add_task(task_name, total=total)

    inserted = 0
    threshold = inserted + every
    for group_id, n, grouped_pairs in sample_grouped_pairs(reference_sets, ref_key):
        try:
            result = reference_sets_pairs[ref_key].insert_many(grouped_pairs)
            inserted += len(result.inserted_ids)
            reference_sets_group_lookup[ref_key].insert_one(
                    dict(group_id=group_id, pair_ids=result.inserted_ids,
                         n=n))
        except pymongo.errors.InvalidOperation:
            pass # Only one element in group, cannot make pairs
        except pymongo.errors.DocumentTooLarge:
            print(f'Document too large for {len(result.inserted_ids)} ids')
        if inserted > limit:
            break
        if inserted > threshold:
            print(f'{inserted:20} in {ref_key:10} ...')
            threshold = inserted + every
        with progress_lock:
            progress.update(task, advance=1)

    return inserted

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

    # ref_keys = reference_sets.list_collection_names()
    # ref_keys = ('match', 'hard_match', 'soft_match', 'differing_last_name', 'last_name')
    ref_keys = ('match', 'differing_last_name', 'last_name')
    threads = len(ref_keys)

    with Progress() as progress:
        with Pool(max_workers=threads) as pool:
            f = partial(sample_for_ref_key, progress=progress,
                        reference_sets=reference_sets,
                        reference_sets_pairs=reference_sets_pairs,
                        reference_sets_group_lookup=reference_sets_group_lookup)
            print(list(pool.map(f, ref_keys)))

    for ref_key in ref_keys:
        print(ref_key, reference_sets_pairs[ref_key].count_documents({}))

