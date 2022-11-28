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
# import plotly.express as px
from collections import OrderedDict

import itertools

from .inference import get_r_table_data, parse_previous_ratios

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
    prev_xi_ratios, prev_interpolated = parse_previous_ratios()

    for label, ratios in [('Current', xi_ratios),
                          ('Previous', prev_xi_ratios)]:
        df = pd.DataFrame([(f, v, np.log(min(r,10))) for (f, v), r in ratios.items()],
                          columns=['feature', 'value', 'ratio'])
        s = sns.lineplot(df, x='value', y='ratio', hue='feature')
        s.set(xlabel='Value', ylabel='Log Ratio', title=f'{label} Log Ratio Table')
        plt.savefig(f'plots/{label.lower()}_ratio_table.png')
        plt.clf()



'''
{
│   ('x1', 0): 0.03216461924326833,
│   ('x1', 1): 0.22928584419119807,
│   ('x1', 2): 214304.46578507224,
│   ('x1', 3): 21.53620993337906,
│   ('x2', 0): 0.997495698316628,
│   ('x2', 1): 1293.9776884016992,
│   ('x7', 0): 2.3314913304535114,
│   ('x7', 1): 0.153159893537048,
│   ('x7', 2): 1.0169196320027893,
│   ('x7', 3): 1651.4730257379042,
│   ('x10', 0): 0.12532655047597785,
│   ('x10', 1): 0.37290735458115865,
│   ('x10', 2): 221.79148114593846,
│   ('x10', 4): 277.84944958783916,
│   ('x10', 5): 12.351431067059824,
│   ('x10', 6): 815.2448018819113,
│   ('x10', 7): 3797.222213531953,
│   ('x10', 8): 45.8526628322524,
│   ('x10', 9): 154.6555915867496,
│   ('x10', 10): 73508.03583031513,
│   ('x10', 11): 1351.7504111715364
}
'''
