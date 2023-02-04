
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
# import plotly.express as px
from collections import OrderedDict

import itertools

from .inference import get_r_table_data, parse_previous_ratios

def run():
    ''' Verify the ratio table and visualize it '''

    get_client('mongo_credentials.json', local=False)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    subsets        = client.reference_sets
    pairs          = client.reference_sets_pairs

    features       = client.features
    feature_groups_a = client.feature_groups_a
    feature_groups_i = client.feature_groups_i

    all_ratios = []

    for source in ('torvik', 'torvik_reported', 'torvik_robust', 'authority_legacy', 'self_citations', 'mixed'):
        xi_ratios, interpolated = get_r_table_data(client.r_table, ratios_from=source)
        print(source)
        print(xi_ratios)
        all_ratios.append((source, xi_ratios))

    for label, ratios in all_ratios:
        print(label)
        df = pd.DataFrame([[int(f.replace('x', '')),
                            v, np.log(np.maximum(r, 1e-4))]
                           for (f, v), r in ratios.items()],
                          columns=['feature', 'value', 'ratio'])
        print(df)
        print(df.dtypes)

        s = sns.scatterplot(df, x='value', y='ratio', hue='feature')
        # s = sns.lineplot(df, x='value', y='ratio', hue='feature')
        s.set(xlabel='Value', ylabel='Log Ratio', title=f'{label} Log Ratio Table')
        plt.savefig(f'plots/{label.lower()}_ratio_table.png')
        plt.show()
        plt.clf()
