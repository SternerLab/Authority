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

from .inference import get_r_table_data

def run():
    ''' Verify the ratio table and visualize it '''

    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    subsets        = client.reference_sets
    pairs          = client.reference_sets_pairs

    features       = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    r_table          = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table)
    pprint(xi_ratios)
    pprint(interpolated)
