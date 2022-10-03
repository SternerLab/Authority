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
                 {'$sort': SON([('_id', 1)])}]
    return pipeline

def generate(pairs, progress, task_name):
    total = pairs.count_documents({})
    with progress_lock:
        task = progress.add_task(task_name, total=total)
    for pair in pairs.find():
        with progress_lock:
            progress.update(task, advance=1)
            yield pair

def insert_features(ref_key, client, progress):

    jstor_database   = client.jstor_database
    articles         = jstor_database.articles
    pairs            = client.reference_sets_pairs
    features         = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    task_name = f'Calculating features for {ref_key}'
    features[ref_key].insert_many(compare_pair(pair, articles)
            for pair in generate(pairs[ref_key], progress, task_name))

    ''' Group by features x_a '''
    pipeline = make_group_pipeline({f'x{i}' : f'$features.x{i}' for i in x_a})
    feature_groups_a[ref_key].insert_many(
        features[ref_key].aggregate(pipeline))

    pipelines = [make_group_pipeline({f'x{i}' : f'$features.x{i}'}) for i in x_i]
    for i, pipeline in enumerate(pipelines):
        group_key = f'{ref_key}_x{i}'
        print(group_key)
        feature_groups_i[group_key].insert_many(
            features[ref_key].aggregate(pipeline))

def run():
    ''' Calculate the features for the different sets in the database '''

    client         = MongoClient('localhost', 27017)

    client.drop_database('features')
    client.drop_database('feature_groups_a')
    client.drop_database('feature_groups_i')

    ''' Create feature vectors for the pair collections '''
    ref_keys = list(client.reference_sets_pairs.list_collection_names())

    threads = 3
    with Progress() as progress:
        with Pool(max_workers=threads) as pool:
            pool.map(partial(insert_features, client=client, progress=progress),
                     ref_keys)
