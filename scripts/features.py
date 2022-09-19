from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
from bson.son import SON
import itertools
from collections import defaultdict

from authority.algorithm.compare import compare

x_a = [3, 4, 5, 6]
limits  = dict(x3=7, x4=1, x5=7, x6=7)
excluded_features = {8, 9}

def compare_pair(pair, articles):
    a, b = pair['pair']
    doc_a = articles.find_one({'_id' : a['ids']})
    doc_b = articles.find_one({'_id' : b['ids']})
    doc_a.update(**a['authors'])
    doc_b.update(**b['authors'])
    feature_dict = compare(doc_a, doc_b)
    for k, l in limits.items():
        feature_dict[k] = min(feature_dict[k], l)
    return dict(pair=[a, b], features=feature_dict)

def run():
    ''' Calculate the features for the different sets in the database
        for features x1, x2, and x7, there are bounds,
        but for features x3-x6, x8, and x9, there are not tight bounds
        so first independent r(x_i) is estimated for bounded features,
            by using a simple ratio of means between matches and non-matches
        and then r(x_i) is estimated for unbounded features
            using smoothing, interpolation, and extrapolation..
        then, r(x_i) for all i can be computed by multiplying each component r(x_i)
    '''

    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs

    client.drop_database('features')
    client.drop_database('feature_groups')
    client.drop_database('feature_groups_a')
    client.drop_database('feature_groups_i')
    client.drop_database('possible_features')

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
    pipeline = [{'$group': {
                 '_id'    : {f'x{i}' : f'$features.x{i}'
                             for i in x_a},
                 'count'  : {'$sum': 1},
                 }},
                 {'$sort': SON([('_id', 1)])}]
    for ref_key in features.list_collection_names():
        feature_groups_a[ref_key].insert_many(
            features[ref_key].aggregate(pipeline))

    # ''' Sum feature vectors by reference set, to estimate frequency '''
    pipelines = [(i, [{'$group': {
                        '_id'    : {f'x{i}' : f'$features.x{i}'},
                        'count'  : {'$sum': 1},
                        }},
                      {'$sort': SON([('_id', 1)])}
                      ]) for i in range(1, 11)
                         if i not in x_a and i not in excluded_features]
    for ref_key in features.list_collection_names():
        for i, pipeline in pipelines:
            group_key = f'{ref_key}_x{i}'
            feature_groups_i[group_key].insert_many(
                features[ref_key].aggregate(pipeline))
