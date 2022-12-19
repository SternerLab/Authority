from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from pathlib import Path

from resolution.algorithm.inference  import *
from resolution.baselines.classifier import *
from resolution.baselines.cluster    import *
from resolution.baselines.embedding  import *

def run():
    '''
    Baselines:
        Naive Bayes
        XGBoost
        Agglomerative Clustering directly on resolution features
        Clustering from SciBERT Features
        Ensemble with both XGBoost and SciBERT

    For each method, we can do either direct clustering (no triplet corrections or agglomerative clustering), or we can use the resolution components
    '''

    client    = MongoClient('localhost', 27017)


    # To do a basic grid search:
    # for cluster_type in ('connected', 'agglomerative'):
    #     for triplets in (True, False):
    methods = [

        Classifier(client, name='naive_bayes_components',
            lookup_name='naive_bayes', correct_triplets=False, reestimate=False,
            hyperparams=dict(method='components')),

        Classifier(client, name='xgboost_components',
            lookup_name='xgboost', correct_triplets=False, reestimate=False,
            hyperparams=dict(method='components'))
        ]

    query = {}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'hedenström'}}
    # query = {'group_id' : {'first_initial' : 'l', 'last' : 'smith'}}
    # query = {'group_id' : {'first_initial' : 'd', 'last' : 'johnson'}}
    inference(client, methods, query=query)
