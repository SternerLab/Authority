from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools
import scipy
import numpy as np

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

    def get_count(group, k, v):
        result = group.find_one({'_id' : {k : v}})
        if result is None:
            return 0
        else:
            return result['count']

    total_matches     = features['match'].count_documents(filter={})
    total_non_matches = features['non_match'].count_documents(filter={})
    ''' Compute r scores by comparing match and non-match frequencies '''
    for p in possible_features.find():
        k, vs = p['k'], p['v']
        match_group     = feature_groups[f'match_{k}']
        non_match_group = feature_groups[f'non_match_{k}']
        n = max(vs)
        x  = np.zeros(len(vs))
        rs = np.zeros(len(vs))
        w  = np.zeros(len(vs))

        for i, v in enumerate(vs):
            match_count     = get_count(match_group, k, v)
            non_match_count = get_count(non_match_group, k, v)
            try:
                r = (match_count / total_matches) / (non_match_count / total_non_matches)
                print(f'{k:3} = {v:2}: {r:4.4f}')
                rs[i] = r
                w[i]  = r
            except ZeroDivisionError:
                print(f'{k}={v}: undefined')
        print(rs)
        def objective(x):
            return w @ (rs - x)**2

        def constraint(x):
            bound = np.concatenate((x[1:], x[-1:]), axis=-1)
            return bound - x

        rh = scipy.optimize.minimize(objective, x, method='slsqp',
                constraints=[dict(type='ineq', fun=constraint)])
        print(rh)



