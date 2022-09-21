from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
from bson.son import SON
from bson.binary import Binary
import itertools
import scipy
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import itertools

from authority.algorithm.compare import compare_pair, x_i, x_a
from authority.algorithm.triplet_violations import fix_triplet_violations

def estimate_prior(n):
    return 1 / (1 + 10**-1.194 * n**0.7975)

def inference(ratio, prior):
    return 1 / (1 + (1 - prior) / (prior * ratio))

def infer_from_feature(features, interpolated, xi_ratios, prior):
    x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
    r_a = interpolated[x3, x4, x5, x6]
    x_i_keys = [f'x{i}' for i in x_i]
    r_is = np.array([xi_ratios[(k, features[k] if features[k] is not None else 0)]
                     for k in x_i_keys])
    ratio = np.prod(r_is) * r_a
    return inference(ratio, prior)

def get_r_table_data(r_table):
    xi_ratios = next(r_table.find({'xi_ratios' : {'$exists' : True}}))
    xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}

    interpolated_doc = next(r_table.find(
                            {'interpolated_xa_ratios' : {'$exists' : True}}))
    interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
    return xi_ratios, interpolated


def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    lookup         = client.reference_sets_group_lookup
    subsets        = client.reference_sets

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table)

    ref_key = 'block'
    for pair_lookup in lookup[ref_key].find():
        group_id = pair_lookup['group_id']
        group = next(subsets[ref_key].find({'_id' : group_id}))

        pair_ids = pair_lookup['pair_ids']
        match_prior = estimate_prior(pair_lookup['n'])
        id_lookup = dict()
        for i, doc in enumerate(group['group']):
            id_lookup[doc['ids']] = i

        m     = len(id_lookup)
        table = np.zeros((m, m))

        for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
            compared = compare_pair(pair, articles)
            features = compared['features']
            p = infer_from_feature(features, interpolated, xi_ratios, match_prior)
            i, j = [id_lookup[doc['ids']] for doc in pair['pair']]
            table[i, j] = p

        pprint(np.sum(table - fix_triplet_violations(table)))

