
import pymongo
from rich.pretty import pprint
from rich.progress import track, Progress
from rich import print
from bson.son import SON
from functools import partial
import itertools
import math

from resolution.authority.compare import compare_pair
from resolution.database.client import get_client

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
        for group_doc in database[ref_key].find(session=session,
                                                no_cursor_timeout=True):
            group_id = group_doc.get('group_id', group_doc['_id'])
            n  = group_doc.get('count', None)
            yield group_id, n, sample_pairs(group_doc['group'])

def sample_mesh_coauthor_non_match_pairs(a, b):
    for pair in itertools.product(a['group'], b['group']):
        a, b = pair
        if a['title'] != b['title']:
            yield dict(pair=pair)

def create_mesh_coauthor_non_match_pairs(client):
    ''' Create non-matching set by sampling articles with different last names '''
    reference_sets = client.reference_sets
    reference_sets_pairs = client.reference_sets_pairs
    reference_sets_group_lookup = client.reference_sets_group_lookup
    # ln_set = reference_sets['last_name'] # Less restrictive
    ln_set = reference_sets['first_initial_last_name'] # More restrictive

    with client.start_session(causal_consistency=True) as session:
        cursor = ln_set.find(session=session, no_cursor_timeout=True)
        for a, b in itertools.combinations(cursor, r=2):
            n = len(a['group']) + len(b['group'])
            group_id = [a['_id'], b['_id']]
            yield group_id, n, sample_mesh_coauthor_non_match_pairs(a, b)

def filter_name_non_match_pairs(pair_generator):
    ''' Filter on "name, language, and nothing else" '''
    for pair in pair_generator:
        comparison   = compare_pair(pair)
        f            = comparison['features']
        lang         = f['x7'] >= 2
        # Only consider *article* features
        # This means less than three MeSH terms, no coauthors, less than two title words
        # These could be made more restrictive, or could include checking language or journal, year, etc
        nothing_else = f['x6'] < 3 and f['x5'] == 1 and f['x3'] < 2
        # and f['x4'] == 0
        # nothing_else = f['x5'] == 0 and f['x1'] != 3 and f['x2'] == 0 and f['x4'] == 0
        # Only consider name features, no x3, x4, x5, x6 etc
        # nothing_else = f['x1'] == 0 and f['x2'] == 0 # and f['x4'] == 0 #?
        if lang and nothing_else:
            yield pair

def create_name_non_match_pairs(client):
    ''' Create "name" non-matching set by sampling articles
        with the SAME names but NO other features in common '''
    generator = sample_grouped_pairs(client, client.reference_sets, 'first_initial_last_name')
    for group_id, n, pair_generator in generator:
        yield group_id, n, filter_name_non_match_pairs(pair_generator)

def filter_first_name_non_match_pairs(pair_generator):
    ''' Filter on "name, language, and nothing else" '''
    for pair in pair_generator:
        a, b = [p['authors']['first'] for p in pair['pair']]
        if a != '' and b != '' and a == b:
            yield pair

def create_first_name_non_match_pairs(client):
    generator = sample_grouped_pairs(client, client.reference_sets, 'first_initial_last_name')
    for group_id, n, pair_generator in generator:
        yield group_id, n, filter_first_name_non_match_pairs(pair_generator)

def sample_for_ref_key(ref_key, client, progress, reference_sets, reference_sets_group_lookup,
                       reference_sets_pairs, every=10000):
    if 'non_match' in ref_key:
        match ref_key:
            case 'mesh_coauthor_non_match':
                generator = create_mesh_coauthor_non_match_pairs(client)
            case 'name_non_match':
                generator = create_name_non_match_pairs(client)
            case 'first_name_non_match':
                generator = create_first_name_non_match_pairs(client)
        limit = float('inf')
        limit = 15000000
        total = limit # Assuming we will run into the limit, which we should
        total = 15000000 # Since it's not obvious how to get this analytically
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
        # except TypeError:
        #     pass # "documents must be a non-empty list" -> filting removed all pairs
        except pymongo.errors.InvalidOperation:
            pass # Only one element in group, cannot make pairs, should be filtered somehow
        except pymongo.errors.DocumentTooLarge:
            print(f'Document too large for {len(result.inserted_ids)} ids')
            print(f'Group id: {group_id}')
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
    get_client('mongo_credentials.json', local=False)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    # Pls no more
    # client.drop_database('reference_sets_pairs')
    # client.drop_database('reference_sets_group_lookup')

    reference_sets_pairs = client.reference_sets_pairs
    reference_sets_group_lookup = client.reference_sets_group_lookup
    reference_sets = client.reference_sets

    total  = articles.count_documents({})

    ref_keys = tuple(reference_sets.list_collection_names())
    ref_keys += ('first_initial_last_name', 'mesh_coauthor_match', 'name_match')
    ref_keys += ('name_non_match', 'mesh_coauthor_non_match')
    ref_keys += ('first_name_non_match',)

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

