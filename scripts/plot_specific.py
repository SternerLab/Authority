import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from rich.progress import track

from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle

from bson.objectid import ObjectId

from authority.validation.metrics import *
from authority.validation.self_citations import resolve, make_contiguous

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['first_initial_last_name']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    # name = 'ajohnson'
    # name = 'jsmith'
    # name = 'jbrown'
    # name = 'dwardle'
    name = 'djohnson'
    first_initial, *last = name
    last = ''.join(last)
    query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}

    print('Validating..')
    print(inferred_blocks.find({}))

    for cluster in inferred_blocks.find(query):
        gid  = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"]}{gid["last"]}'

        print(cluster)
        for feature_key, (p, r, rs_b, c) in cluster['feature_analysis'].items():
            features = tuple(int(x) for x in feature_key.split(' '))
            rs = pickle.loads(rs_b)
            print(f'{features} {p} {r}')
            print(rs)
        # print(cluster['feature_analysis'])
        # 1/0

        print(cluster['match_prior'])
        print(cluster['prior'])
        for cluster_key, title in (('original_probs', 'Original Probabilities'),
                                   ('fixed_probs', 'Triplet Corrected Probabilities'),
                                   ('probs',       'Final Probabilities'),
                                   ('ratios',      'Ratio table')):
            data = pickle.loads(cluster[cluster_key])
            if cluster_key == 'ratios':
                data = np.where(data > 0., np.log(data), data)
            print(cluster_key, title)
            print(data)
            axe = sns.heatmap(data)
            axe.set_title(f'{title} for {name}')
            axe.set_xlabel('Papers')
            axe.set_ylabel('Papers')
            plt.savefig(f'plots/{key}_{title.replace(" ", "_").lower()}.png')
            plt.show()
            plt.clf()
