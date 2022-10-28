from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track, Progress
from rich import print
from bson.son import SON
from functools import partial
import itertools
import math

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def sample_pairs(group):
    accepted  = 0
    rejected  = 0
    for pair in itertools.combinations(group, r=2):
        mesh_a, mesh_b = (p['mesh'] for p in pair)
        assert isinstance(mesh_a, list) and isinstance(mesh_b, list), 'MeSH already processed'
        yield dict(pair=pair)

def sample_grouped_pairs(client, database, ref_key):
    total = database[ref_key].count_documents({})
    with client.start_session(causal_consistency=True) as session:
        for group_doc in database[ref_key].find(session=session, no_cursor_timeout=True):
            group_id = group_doc['_id']
            n  = group_doc.get('count', None)
            yield group_id, n, sample_pairs(group_doc['group'])

def sample_non_match_pairs(a, b):
    for pair in itertools.product(a['group'], b['group']):
        yield dict(pair=pair)

def create_non_match_pairs(client):
    ''' Create non-matching set by sampling articles with different last names '''
    reference_sets = client.reference_sets
    reference_sets_pairs = client.reference_sets_pairs
    reference_sets_group_lookup = client.reference_sets_group_lookup
    filn_set = reference_sets['first_initial_last_name']

    with client.start_session(causal_consistency=True) as session:
        cursor = filn_set.find(session=session, no_cursor_timeout=True)
        for a, b in itertools.combinations(cursor, r=2):
            n = len(a['group']) + len(b['group'])
            group_id = [a['_id'], b['_id']]
            yield group_id, n, sample_non_match_pairs(a, b)

def sample_for_ref_key(ref_key, client, progress, reference_sets, reference_sets_group_lookup,
                       reference_sets_pairs, every=10000):
    if ref_key == 'non_match':
        limit = reference_sets_pairs['match'].count_documents({}) # Limit to number of pairs in match set
        limit *= 4
        generator = create_non_match_pairs(client)
        total = limit # Assuming we will run into the limit, which we should
    else:
        limit = float('inf')
        generator = sample_grouped_pairs(client, reference_sets, ref_key)
        total = reference_sets[ref_key].count_documents({})

    task_name = f'Sampling pairs from {ref_key}'
    task  = progress.add_task(task_name, total=min(total, limit))

    inserted = 0
    threshold = inserted + every
    for group_id, n, grouped_pairs in generator:
        try:
            result = reference_sets_pairs[ref_key].insert_many(grouped_pairs)
            inserted += len(result.inserted_ids)
            reference_sets_group_lookup[ref_key].insert_one(
                    dict(group_id=group_id, pair_ids=result.inserted_ids, n=n))
        except pymongo.errors.InvalidOperation:
            pass # Only one element in group, cannot make pairs, should be filtered somehow
        except pymongo.errors.DocumentTooLarge:
            print(f'Document too large for {len(result.inserted_ids)} ids')
        if inserted > limit:
            print(f'Reaching upper limit {limit}')
            break
        if inserted > threshold:
            print(f'{inserted:20} in {ref_key:10} ...')
            threshold = inserted + every
        progress.update(task, advance=1)
    return inserted

def run():
    ''' Use the reference sets to create pairs of articles in a new database '''
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    # client.drop_database('reference_sets_pairs')
    # client.drop_database('reference_sets_group_lookup')

    reference_sets_pairs = client.reference_sets_pairs
    reference_sets_group_lookup = client.reference_sets_group_lookup
    reference_sets = client.reference_sets

    total  = articles.count_documents({})

    ref_keys = reference_sets.list_collection_names()
    # ref_keys = ('first_initial_last_name', 'match', 'non_match')
    # ref_keys = ('match', 'non_match') # Order matters
    ref_keys = ('hard_match', 'soft_match', 'non_match',)

    with Progress() as progress:
        for ref_key in ref_keys:
            reference_sets_pairs.drop_collection(ref_key)
            reference_sets_group_lookup.drop_collection(ref_key)
            sample_for_ref_key(ref_key, client=client,
                        progress=progress,
                        reference_sets=reference_sets,
                        reference_sets_pairs=reference_sets_pairs,
                        reference_sets_group_lookup=reference_sets_group_lookup)

    for ref_key in ref_keys:
        print(ref_key, reference_sets_pairs[ref_key].count_documents({}))

