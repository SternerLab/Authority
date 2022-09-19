from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
from bson.son import SON
import itertools
from collections import defaultdict

from authority.algorithm.compare import compare_pair, x_a, x_i, limits, excluded

def make_group_pipeline(feature_dict):
    pipeline = [{'$group': {
                 '_id'    : feature_dict,
                 'count'  : {'$sum': 1},
                 }},
                 {'$sort': SON([('_id', 1)])}]

def run():
    ''' Calculate the features for the different sets in the database '''

    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs

    client.drop_database('features')
    client.drop_database('feature_groups_a')
    client.drop_database('feature_groups_i')

    features       = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    ''' Create feature vectors for the pair collections '''
    for ref_key in pairs.list_collection_names():
        print(ref_key)
        features[ref_key].insert_many(
            compare_pair(pair, articles) for pair in track(pairs[ref_key].find(),
                description=f'Calculating features for {ref_key}',
                total=pairs[ref_key].count_documents({})))

    ''' Group by features x_a '''
    pipeline = make_group_pipeline({f'x{i}' : f'$features.x{i}' for i in x_a})
    for ref_key in features.list_collection_names():
        feature_groups_a[ref_key].insert_many(
            features[ref_key].aggregate(pipeline))

    # ''' Sum feature vectors by reference set, to estimate frequency '''
    pipelines = [make_group_pipeline({f'x{i}' : f'$features.x{i}'}) for i in x_i]
    for ref_key in features.list_collection_names():
        for i, pipeline in pipelines:
            group_key = f'{ref_key}_x{i}'
            feature_groups_i[group_key].insert_many(
                features[ref_key].aggregate(pipeline))
