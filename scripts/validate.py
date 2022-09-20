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

    # for bhl_cluster in bhl.find():
    #     key = bhl_cluster['author']['key']
    #     print(key)
    #     for pair in pairs['match'].find({'pair' : {'authors' : {'key' : key}}}):
    #         print('bhl cluster')
    #         pprint(bhl_cluster)
    #         print('pair')
    #         pprint(pair)
    # 1/0


    n = 1000
    match_prior = 1/11 # for testing, bad :)
    for group in ('match', 'non_match', 'block'):
        print(group)
        ps = []
        i = 0
        for pair in pairs[group].find():
            if i == n:
                break
            try:
                # pprint(pair)
                compared = compare_pair(pair, articles)
                features = compared['features']
                p = infer_from_feature(features, interpolated, xi_ratios, match_prior)
                # print(p)
                ps.append(p)
            except KeyError:
                pass
            i += 1
        print(group, sum(ps) / n)
