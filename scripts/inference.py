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

def estimate_prior(n):
    return 1 / (1 + 10**-1.194 * n**0.7975)

def inference(ratio, prior):
    return 1 / (1 + (1 - prior) / (prior * ratio))

def infer_from_feature(features, interpolated, xi_ratios, prior):
    x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
    r_a = interpolated[x3, x4, x5, x6]
    x_i_keys = [f'x{i}' for i in x_i]
    r_is = np.array([xi_ratios[(k, features[k])] for k in x_i_keys])
    ratio = np.prod(r_is) * r_a
    return inference(ratio, prior)

def get_r_table_data(r_table):
    xi_ratios = next(r_table.find({'xi_ratios' : {'$exists' : True}}))
    xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}

    interpolated_doc = next(r_table.find({'interpolated_xa_ratios' : {'$exists' : True}}))
    interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
    return xi_ratios, interpolated

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    subsets        = client.reference_sets

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table)

    for pair in pairs['block'].find():
        try:
            n = pair['n'] # Defined for all but non-match sets
            match_prior = estimate_prior(n)
            compared = compare_pair(pair, articles)
            features = compared['features']
            print(infer_from_feature(features, interpolated, xi_ratios, match_prior))
        except KeyError:
            pass
