from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track, Progress
from bson.son import SON
import itertools
from collections import defaultdict
from functools import partial
from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock
progress_lock = Lock()

from authority.algorithm.compare import compare_pair, x_a, x_i, limits

def make_group_pipeline(feature_dict):
    pipeline = [{'$group': {
                 '_id'    : feature_dict,
                 'count'  : {'$sum': 1},
                 }},
                 # {'$sort': SON([('_id', 1)])}
                 ]
    return pipeline

def generate(pairs, progress, task_name, limit=None):
    ref_key = task_name.split(' ')[-1]
    if limit is not None:
        total = limit
    else:
        total = pairs.count_documents({})
    print(f'Task {task_name} has upper bound of {total} pairs!')
    with progress_lock:
        task = progress.add_task(task_name, total=total)
    accepted = 0
    rejected = 0
    for pair in pairs.find():
        if accepted + rejected == limit: # TODO Rejection ignored for now
            break
        # if accepted == limit:
        #     break
        mesh_a, mesh_b = (p['mesh'] for p in pair['pair'])
        if isinstance(mesh_a, list) and isinstance(mesh_b, list):
            accepted += 1
        else:
            rejected += 1
        with progress_lock:
            progress.update(task, advance=1)
        yield pair
        # TODO Rejection based on MeSH terms is intentionally ignored for now
        print(f'{ref_key:20} rejected {rejected:5} accepted {accepted:5}')


def insert_features(ref_key, client, progress, limit=None, batch_size=128):

    jstor_database   = client.jstor_database
    articles         = jstor_database.articles
    pairs            = client.reference_sets_pairs
    features         = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    task_name = f'Calculating features for {ref_key}'
    generator = generate(pairs[ref_key], progress, task_name, limit)
    while True:
        batch = list(itertools.islice(generator, batch_size))
        if len(batch) == 0:
            break
        features[ref_key].insert_many(compare_pair(pair, articles) for pair in batch)

    ''' Group by features x_a '''
    pipeline = make_group_pipeline({f'x{i}' : f'$features.x{i}' for i in x_a})
    feature_groups_a[ref_key].insert_many(
        features[ref_key].aggregate(pipeline))

    pipelines = [make_group_pipeline({f'x{i}' : f'$features.x{i}'}) for i in x_i]
    for i, pipeline in zip(x_i, pipelines): # Fixed!
        group_key = f'{ref_key}_x{i}'
        feature_groups_i[group_key].insert_many(
            features[ref_key].aggregate(pipeline))

def run():
    ''' Calculate the features for the different sets in the database '''

    client         = MongoClient('localhost', 27017)


    ''' Create feature vectors for the pair collections '''
    ref_keys = list(client.reference_sets_pairs.list_collection_names())
    print(ref_keys)

    client.drop_database('features')
    client.drop_database('feature_groups_a')
    client.drop_database('feature_groups_i')

    limit = None
    # limit = 2000000 # Reasonable
    # limit = 1000000 # stricter
    # limit = 200000

    threads = len(ref_keys)
    with Progress() as progress:
        f = partial(insert_features, client=client, progress=progress, limit=limit)
        with Pool(max_workers=threads) as pool:
            results = pool.map(f, ref_keys)
            print(list(results))
