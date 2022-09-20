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

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    r_table          = client.r_table.r_table

    bhl_database   = client.bhl_database
    bhl            = bhl_database.bhl

    xi_ratios, interpolated = get_r_table_data(r_table)

    match_prior = 1/11 # for testing, bad :)
    for pair in pairs['block'].find():
        try:
            pprint(pair)
            compared = compare_pair(pair, articles)
            features = compared['features']
            print(infer_from_feature(features, interpolated, xi_ratios, match_prior))
        except KeyError:
            pass
