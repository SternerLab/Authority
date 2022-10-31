import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from rich.progress import track

from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd

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

    name = 'ajohnson'
    first_initial, *last = name
    last = ''.join(last)
    query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}

    print('Validating..')
    print(inferred_blocks.find({}))

    # probs=binary_probs, prior=new_prior,
    # match_prior=match_prior, group_id=group_id))

    for cluster in inferred_blocks.find(query):
        probs = pickle.loads(cluster['original_probs'])
        pprint(cluster.keys())
        print(cluster['prior'])
        print(probs)
        sns.heatmap(probs)
        plt.show()
        plt.clf()

        ratios = pickle.loads(cluster['ratios'])
        sns.heatmap(ratios)
        plt.show()
