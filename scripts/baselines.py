from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from pathlib import Path

from resolution.algorithm.inference  import *
from resolution.baselines.classifier import *
from resolution.baselines.embedding  import *

def run():
    '''
    Baselines:
        Naive Bayes
        XGBoost
        Clustering from SciBERT Features
        Ensemble with both XGBoost, SciBERT, and Authority

    For each method, we can do either direct clustering (no triplet corrections or agglomerative clustering), or we can use the resolution components
    '''

    client    = MongoClient('localhost', 27017)


    # To do a basic grid search:
    # for cluster_type in ('connected', 'agglomerative'):
    #     for triplets in (True, False):
    methods = [

        # Both clustering methods behaved identically
        EmbeddingClusterer(client, name='scibert_clustering',
            hyperparams=dict(method='hdbscan', model='allenai/scibert_scivocab_uncased',
                             epsilon=0.6)),

        # EmbeddingClusterer(client, name='scidebert_clustering',
        #     hyperparams=dict(method='hdbscan', model='KISTI-AI/scideberta')),

        # Classifier(client, name='naive_bayes',
        #     lookup_name='naive_bayes',
        #            correct_triplets=False, reestimate=False,
        #     hyperparams=dict(method='components')),

        # Classifier(client, name='xgboost',
        #     lookup_name='xgboost',
        #            correct_triplets=False, reestimate=False,
        #     hyperparams=dict(method='components')),

        ]

    query = {}
    # query = {'group_id.first_initial' : 'a'}
    # query = {'group_id.last' : 'smith'}
    # query = {'group_id.last' : 'johnson'}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'hedenström'}}
    # query = {'group_id' : {'first_initial' : 'l', 'last' : 'smith'}}
    # query = {'group_id' : {'first_initial' : 'd', 'last' : 'johnson'}}
    # query = {'group_id' : {'first_initial' : 'j', 'last': 'smith'}}
    inference(client, methods, query=query, drop=True)
