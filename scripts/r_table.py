from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
from bson.son import SON
import itertools
import scipy
import numpy as np

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

    def get_count(group, k, v):
        result = group.find_one({'_id' : {k : v}})
        if result is None:
            return 0
        else:
            return result['count']

    total_matches     = features['match'].count_documents(filter={})
    total_non_matches = features['non_match'].count_documents(filter={})

    limits  = dict(x3=7, x4=1, x5=7, x6=7, x9=1)
    r_table = {k : np.zeros(l + 1) for k, l in limits.items()}

    ''' Compute r scores by comparing match and non-match frequencies '''
    for p in possible_features.find():
        k, vs = p['k'], p['v']
        match_group     = feature_groups[f'match_{k}']
        non_match_group = feature_groups[f'non_match_{k}']
        l  = len(vs)
        x  = np.zeros(l)
        rs = np.zeros(l)
        w  = np.zeros(l)

        for i, v in enumerate(vs):
            match_count     = get_count(match_group, k, v)
            non_match_count = get_count(non_match_group, k, v)
            try:
                r = (match_count / total_matches) / (non_match_count / total_non_matches)
                # print(f'{k:3} = {v:2}: {r:4.4f}')
                rs[i] = r
                w[i]  = match_count + non_match_count
            except ZeroDivisionError:
                print(f'{k}={v}: undefined') # will stay at initial 0 state
        # print(rs)
        def objective(x):
            return w @ (rs - x)**2

        def constraint(x):
            bound = np.concatenate((x[1:], x[-1:]), axis=-1)
            return bound - x # since this needs to be positive, it constrains to monotonicity

        rh = scipy.optimize.minimize(objective, x, method='slsqp',
                constraints=[dict(type='ineq', fun=constraint)])['x']
        for i, (ro, rs, v) in enumerate(zip(rs, rh, vs)):
            if v is None:
                print(f'{k:3} = None: {rs:4.4f} ({ro:4.4f})')
            else:
                print(f'{k:3} = {v:2}: {rs:4.4f} ({ro:4.4f})')
            if k in limits and v <= limits[k]:
                r_table[k][v] = rs
    pprint(r_table)
    1/0

    ''' Interpolation '''
    for (x3, x4, x5, x6, x9) in itertools.product(
            *(range(l) for l in limits)):

        print(x3, x4, x5, x6, x9)



