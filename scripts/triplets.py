import numpy as np

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

from .inference import *
from authority.algorithm.triplet_violations import fix_triplet_violations

# def run():
#     print('Testing triplet violation code')
#     # let triplet be [pij pjk pik]
#     triplet = np.array([0.1, 0.1, 0.9])
#     delta = 0.05
#     print(triplet)
#     print(triplet[0] + triplet[1], triplet[2] + delta)
#     fixed = fix_triplet_violations(triplet)
#     print(fixed)

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    subsets        = client.reference_sets
    r_table        = client.r_table.r_table

    xi_ratios, interpolated = get_r_table_data(r_table)

    n = 1000
    match_prior = 1/11 # for testing, bad :)
    for ref_key in ('match', 'non_match', 'block'):
        for element in subsets[ref_key].find():
            group_id = element['_id']
            for pair in pairs[ref_key].find({'group_id' : group_id}):
                pprint(pair)
        # print(group)
        # ps = []
        # i = 0
        # for pair in pairs[group].find():
        #     pprint(pair)
        #     1/0
        #     if i == n:
        #         break
        #     try:
        #         # pprint(pair)
        #         compared = compare_pair(pair, articles)
        #         features = compared['features']
        #         p = infer_from_feature(features, interpolated, xi_ratios, match_prior)
        #     except KeyError:
        #         pass
        #     i += 1
        # print(group, sum(ps) / n)
