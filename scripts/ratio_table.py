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
from collections import OrderedDict, namedtuple
import logging
import itertools

log = logging.getLogger('rich')

from resolution.authority import compute_ratios, compute_xi_ratios, smooth, interpolate
from resolution.authority.compare import *

Split = namedtuple('Split', ['meta_pos', 'meta_neg', 'article_pos', 'article_neg'])

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

    r_table          = client.r_table

    # Define the splits from Torvik 2005/2009/2014, as well as experimental ones
    self_supervision_splits = {'torvik':
                               Split('mesh_coauthor_match', 'mesh_coauthor_non_match',
                                     'name_match', 'name_non_match'),
                               'torvik_robust' :
                               Split('mesh_coauthor_match', 'mesh_coauthor_non_match',
                                     'name_match', 'first_name_non_match'),
                               'self_citations' :
                               Split('self_citations', 'first_name_non_match',
                                     'self_citations',      'first_name_non_match'),
                               'mixed' :
                               Split('mesh_coauthor_match', 'first_name_non_match',
                                     'self_citations',      'first_name_non_match'),
                               }

    # x1, x2, x10 are *name* features, known as x_i here.
    # x7 is the *language* feature, included in x_i here?
    # x3, x4, x5, x6 are *article* features, known as x_a here.

    for name, split in self_supervision_splits.items():
        log.info(f'Computing ratios using the split from {name}')
        r_table.drop_collection(name)
        split_table = r_table[name]

        xi_ratios = compute_xi_ratios(features, feature_groups_i, x_i=x_i,
                                      match=split.meta_pos, non_match=split.meta_neg)
        xi_ratios = [(k, v[0], l) for (k, v), l in xi_ratios.items()]
        split_table.insert_one(dict(xi_ratios=xi_ratios))
        pprint(xi_ratios)

        computed_ratios = compute_ratios(features, feature_groups_a,
                                         match=split.article_pos,
                                         non_match=split.article_neg)
        smoothed        = smooth(computed_ratios)
        interpolated    = interpolate(smoothed)

        xa_ratios = [dict(key=k, value=v) for k, v in computed_ratios.items()]
        smoothed  = [dict(key=k, value=v) for k, v in smoothed.items()]

        split_table.insert_one(dict(xa_ratios=xa_ratios))
        split_table.insert_one(dict(smoothed_xa_ratios=smoothed))
        binary_interpolated = Binary(pickle.dumps(interpolated), subtype=128)
        split_table.insert_one(dict(interpolated_xa_ratios=binary_interpolated))


