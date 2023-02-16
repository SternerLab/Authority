import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from pathlib import Path

from resolution.algorithm.inference  import *
from resolution.baselines.classifier import *
from resolution.baselines.embedding  import *

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)

    '''
    Baselines:
        Naive Bayes
        XGBoost
        Clustering from SciBERT Features
        Ensemble with both XGBoost, SciBERT, and Authority

    For each method, we can do either direct clustering (no triplet corrections or agglomerative clustering), or we can use the resolution components
    '''


    # To do a basic grid search:
    # for cluster_type in ('connected', 'agglomerative'):
    #     for triplets in (True, False):
    methods = [

        # Both clustering methods behaved identically
        # EmbeddingClusterer(client, name='scibert_clustering',
        #     hyperparams=dict(method='hdbscan', model='allenai/scibert_scivocab_uncased',
        #                      epsilon=0.6)),

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

    variants = [f'_{source}{balanced}' for source in
                ['self_citations', 'authority_heuristics', 'both']
                for balanced in ['', '_balanced']]

    for alg in ['xgboost', 'naive_bayes']:
        for variant in variants:
            name = alg + variant
            methods.append(Classifier(client, name=name, lookup_name=name,
                                      correct_triplets=False, reestimate=False, hyperparams=dict(method='components')))
            methods.append(Classifier(client, name=f'{name}_agglomerative', lookup_name=name,
                                      correct_triplets=True, reestimate=True, hyperparams=dict(method='agglomerative')))


    query = {}
    # query = {'group_id.first_initial' : 'a'}
    # query = {'group_id.last' : 'smith'}
    # query = {'group_id.last' : 'johnson'}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'hedenström'}}
    # query = {'group_id' : {'first_initial' : 'l', 'last' : 'smith'}}
    # query = {'group_id' : {'first_initial' : 'd', 'last' : 'johnson'}}
    # query = {'group_id' : {'first_initial' : 'j', 'last': 'smith'}}
    inference(client, methods, query=query, drop=True)
