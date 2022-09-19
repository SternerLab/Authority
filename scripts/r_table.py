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

from authority.algorithm import compute_ratios, smooth, interpolate

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

    computed_ratios = compute_ratios(features, feature_groups_a)
    smoothed = smooth(computed_ratios)
    interpolated = interpolate(smoothed)
    pprint(interpolated)

