from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
from bson.son import SON
from bson.binary import Binary
import itertools
import scipy
import dill as pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict

import itertools

from resolution.authority import compute_ratios, compute_xi_ratios, smooth, interpolate
from resolution.authority.compare import *

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
    subsets        = client.reference_sets
    pairs          = client.reference_sets_pairs

    features       = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    client.drop_database('r_table')
    r_table          = client.r_table.r_table

    # x1, x2, x10 are *name* features, known as x_i here.
    # x7 is the *language* feature, included in x_i here?
    # x3, x4, x5, x6 are *article* features, known as x_a here.

    xi_ratios = compute_xi_ratios(features, feature_groups_i, x_i=x_i, match_type='mesh_coauthor_match', non_match_type='mesh_coauthor_non_match')
    xi_ratios = [(k, v[0], l) for (k, v), l in xi_ratios.items()]
    r_table.insert_one(dict(xi_ratios=xi_ratios))
    pprint(xi_ratios)

    computed_ratios = compute_ratios(features, feature_groups_a, match_type='name_match', non_match_type='name_non_match')
    smoothed        = smooth(computed_ratios)
    interpolated    = interpolate(smoothed)

    xa_ratios = [dict(key=k, value=v) for k, v in computed_ratios.items()]
    smoothed  = [dict(key=k, value=v) for k, v in smoothed.items()]
    r_table.insert_one(dict(xa_ratios=xa_ratios))
    r_table.insert_one(dict(smoothed_xa_ratios=smoothed))
    binary_interpolated = Binary(pickle.dumps(interpolated), subtype=128)
    r_table.insert_one(dict(interpolated_xa_ratios=binary_interpolated))


