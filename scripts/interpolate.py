from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
from bson.son import SON
import itertools
import scipy
import numpy as np

def run():
    ''' Interpolate values within the r table using averaging '''
    client         = MongoClient('localhost', 27017)
    r_table        = client.r_table.r_table
    1/0

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
                print(f'{k}={v}: undefined')
        # print(rs)
        def objective(x):
            return w @ (rs - x)**2

        def constraint(x):
            bound = np.concatenate((x[1:], x[-1:]), axis=-1)
            return bound - x # since this needs to be positive, it constrains to monotonicity

        rh = scipy.optimize.minimize(objective, x, method='slsqp',
                constraints=[dict(type='ineq', fun=constraint)])['x']
        for i, (ro, rs, v) in enumerate(zip(rs, rh, vs)):
            print(f'{k:3} = {v:2}: {rs:4.4f} ({ro:4.4f})')
        # print(rh)



