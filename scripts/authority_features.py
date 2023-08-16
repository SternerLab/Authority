
from rich.pretty import pprint
from rich.progress import track, Progress
from bson.son import SON
import itertools
from collections import defaultdict
from functools import partial
from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock
progress_lock = Lock()

from resolution.authority.compare import compare_pair, x_a, x_i, limits

def make_group_pipeline(feature_dict):
    pipeline = [# {'$limit' : 1000},
                {'$group': {
                 '_id'    : feature_dict,
                 'count'  : {'$sum': 1},
                 }},
                 # {'$sort': SON([('_id', 1)])}
                 ]
    return pipeline

def generate(client, pairs, progress, task_name, limit=float('inf')):
    ref_key = task_name.split(' ')[-1]
    total = pairs.count_documents({})
    print(f'Task {task_name} has upper bound of {total} pairs!')
    task = progress.add_task(task_name, total=total)
    count = 0
    with client.start_session(causal_consistency=True) as session:
        for pair in pairs.find(no_cursor_timeout=True, session=session):
            progress.update(task, advance=1)
            count += 1
            if count < limit:
                yield pair
            else:
                break

def insert_features(ref_key, client, progress, batch_size=128, limit=float('inf')):

    jstor_database   = client.jstor_database
    articles         = jstor_database.articles
    pairs            = client.reference_sets_pairs
    features         = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    task_name = f'Calculating features for {ref_key}'
    generator = generate(client, pairs[ref_key], progress, task_name, limit=limit)
    features.drop_collection(ref_key) # Fixed! Cannot go in loop
    while True:
        batch = list(itertools.islice(generator, batch_size))
        if len(batch) == 0:
            break
        features[ref_key].insert_many(compare_pair(pair) for pair in batch)

    ''' Group by features x_a '''
    pipeline = make_group_pipeline({f'x{i}' : f'$features.x{i}' for i in x_a})
    feature_groups_a.drop_collection(ref_key)
    feature_groups_a[ref_key].insert_many(
        features[ref_key].aggregate(pipeline))

    pipelines = [make_group_pipeline({f'x{i}' : f'$features.x{i}'}) for i in x_i]
    for i, pipeline in zip(x_i, pipelines): # Fixed!
        group_key = f'{ref_key}_x{i}'
        feature_groups_i.drop_collection(group_key)
        feature_groups_i[group_key].insert_many(
            features[ref_key].aggregate(pipeline))

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    ''' Calculate the features for the different sets in the database '''
    pairs  = client.reference_sets_pairs

    ''' Create feature vectors for the pair collections '''
    ref_keys = list(client.reference_sets_pairs.list_collection_names())
    # ref_keys = ('self_citations',)
    print(ref_keys)
    # Don't drop databases, just drop collections to enable partially recreating
    # client.drop_database('features')
    # client.drop_database('feature_groups_a')
    # client.drop_database('feature_groups_i')

    limit = float('inf')
    with Progress() as progress:
        for ref_key in ref_keys:
            insert_features(ref_key, client=client, progress=progress, limit=limit)
        assert client.features[ref_key].count_documents({}) == pairs[ref_key].count_documents({}), f'Number of features does not match number of pairs'
