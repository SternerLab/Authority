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
from .features import x_a, limits

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
    feature_groups_a = client.feature_groups_a
    r_table_coll     = client.r_table.r_table

    def get_count(group, feature):
        result = group.find_one({'_id' : feature})
        if result is None:
            return 0
        else:
            return result['count']

    total_matches     = features['match'].count_documents(filter={})
    total_non_matches = features['non_match'].count_documents(filter={})


    ''' Compute r scores by comparing match and non-match frequencies '''
    # unique_features = OrderedDict()
    unique_features = []
    for ref_key in features.list_collection_names():
        for group in feature_groups_a[ref_key].find():
            key = tuple(group['_id'].values())
            # unique_features[key] = group['_id']
            unique_features.append(key)
    sorted_features = [{f'x{i}' : f for i, f in zip(x_a, fs)}
                       for fs in sorted(unique_features)]

    l  = len(unique_features)
    rs = []
    ws = []

    computed_features = OrderedDict()

    for i, feature in enumerate(sorted_features):
        match_group     = feature_groups_a[f'match']
        non_match_group = feature_groups_a[f'non_match']

        match_count     = get_count(match_group, feature)
        non_match_count = get_count(non_match_group, feature)
        try:
            r = (match_count / total_matches) / (non_match_count / total_non_matches)
            rs.append(r)
            ws.append(match_count + non_match_count)
            key = tuple(feature.values())
            computed_features[key] = r
        except ZeroDivisionError:
            pass

    ''' Smoothing '''
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

    for i, k in enumerate(computed_features):
        computed_features[k] = rh[i]

    ''' Interpolation '''

    interpolated = np.zeros(tuple((l + 1 for l in limits.values())))
    profiles = list(computed_features.items())
    pprint(profiles)
    lower_profile, lower_r = profiles[0]
    upper_profile, upper_r = profiles[-1]
    print('lower', lower_profile, lower_r)
    print('upper', upper_profile, upper_r)

    i = 0
    preceeding = None
    preceeding_r = lower_r
    succeeding = lower_profile
    succeeding_r = lower_r

    for key in itertools.product(*(np.arange(l + 1) for l in limits.values())):
        x3, x4, x5, x6 = key
        if key > succeeding:
            if (i + 1) < len(profiles):
                preceeding, preceeding_r = profiles[i]
                succeeding, succeeding_r = profiles[i + 1]
                i += 1
            else:
                preceeding, preceeding_r = profiles[-1]
                succeeding, succeeding_r = profiles[-1]
        interpolated[x3, x4, x5, x6] = (preceeding_r + succeeding_r) / 2
    pprint(interpolated)

    1/0
