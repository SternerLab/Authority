from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
from bson.son import SON
import itertools
import scipy
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict

import itertools

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

    features       = client.features
    feature_groups = client.feature_groups
    possible_features = client.possible_features.possible_features
    r_table_coll   = client.r_table.r_table

    def get_count(group, feature):
        result = group.find_one({'_id' : feature})
        if result is None:
            return 0
        else:
            return result['count']

    total_matches     = features['match'].count_documents(filter={})
    total_non_matches = features['non_match'].count_documents(filter={})

    x_a = [3, 4, 5, 6]
    limits  = dict(x3=7, x4=1, x5=7, x6=7)

    ''' Compute r scores by comparing match and non-match frequencies '''
    # unique_features = OrderedDict()
    unique_features = []
    for ref_key in features.list_collection_names():
        for group in feature_groups[ref_key].find():
            key = tuple(sorted(group['_id'].values()))
            # unique_features[key] = group['_id']
            unique_features.append(key)
    sorted_features = [{f'x{i}' : f for i, f in zip(x_a, fs)}
                       for fs in sorted(unique_features)]

    l  = len(unique_features)
    rs = []
    ws = []

    for i, feature in enumerate(sorted_features):
        match_group     = feature_groups[f'match']
        non_match_group = feature_groups[f'non_match']

        match_count     = get_count(match_group, feature)
        non_match_count = get_count(non_match_group, feature)
        try:
            r = (match_count / total_matches) / (non_match_count / total_non_matches)
            print(r, match_count, non_match_count)
            rs.append(r)
            ws.append(match_count + non_match_count)
        except ZeroDivisionError:
            pass

    x  = np.zeros(len(rs))
    ws = np.array(ws)
    rs = np.array(rs)

    def objective(x):
        return ws @ (rs - x)**2

    def constraint(x):
        bound = np.concatenate((x[1:], x[-1:]), axis=-1)
        # since this needs to be positive, it constrains to monotonicity
        return bound - x

    rh = scipy.optimize.minimize(objective, x, method='slsqp',
            constraints=[dict(type='ineq', fun=constraint)])['x']
    pprint(rh)
    1/0
    # for i, (ro, rs, v) in enumerate(zip(rs, rh, vs)):
    #     # if v is None:
    #     #     print(f'{k:3} = None: {rs:4.4f} ({ro:4.4f})')
    #     # else:
    #     #     print(f'{k:3} = {v:2}: {rs:4.4f} ({ro:4.4f})')
    #     if k in limits and v <= limits[k]:
    #         r_values[k][v] = rs
    #     smooth_pairs.append((k, v, rs))

    # for source, ps in (('empirical', pairs), ('smoothed', smooth_pairs)):
    #     pprint(r_values)
    #     long = dict(feature=[p[0] for p in ps],
    #                 value=[p[1]   for p in ps],
    #                 r=[p[2]       for p in ps])
    #     df = pd.DataFrame(long)
    #     print(df)
    #     fig = sns.lineplot(df, x='value', y='r', hue='feature', style='feature')
    #     fig.set_title(f'{source.title()} R Values')
    #     fig.figure.savefig(f'plots/{source}_full.png')
    #     fig.set_xlim(0, 5)
    #     fig.set_ylim(0, 10)
    #     fig.figure.savefig(f'plots/{source}_lim.png')
    #     del fig
    #     # fig.set_yscale('log')
    #     # print(dir(fig))

    #     # plt.show()
    # 1/0

    # ''' Interpolation '''
    # for (x3, x4, x5, x6, x9) in itertools.product(
    #         *(range(l) for l in limits)):

    #     print(x3, x4, x5, x6, x9)




