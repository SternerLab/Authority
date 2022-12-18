from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from bson.son import SON
from bson.binary import Binary
import itertools
import json
import scipy
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

import itertools

from resolution.authority.compare import compare_pair, x_i, x_a
from resolution.authority.triplet_violations import fix_triplet_violations
from resolution.authority.clustering import cluster as custom_cluster_alg

from sklearn.cluster import AgglomerativeClustering

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    lookup         = client.reference_sets_group_lookup
    subsets        = client.reference_sets

    baselines = client.baselines

    # Baselines:
    # Naive Bayes
    # XGBoost
    # Agglomerative Clustering directly on resolution features
    # Clustering from SciBERT Features
    # Ensemble with both XGBoost and SciBERT

    # For each method, we can do either direct clustering (no triplet corrections or agglomerative clustering), or we can use the resolution components

    query = {}
    with client.start_session(causal_consistency=True) as session:
        # ref_key = 'last_name'
        ref_key = 'first_initial_last_name'
        total = lookup[ref_key].count_documents({})
        print(f'Performing inference across {total} documents')
        for pair_lookup in track(lookup[ref_key].find(query, session=session,
                                 no_cursor_timeout=True), total=total,
                                 description='Clustering first initial last name blocks'):
            group_id = pair_lookup['group_id']
            group = next(subsets[ref_key].find({'_id' : group_id}))

            pair_ids = pair_lookup['pair_ids']
            match_prior = estimate_prior(pair_lookup['n'])
            id_lookup = dict()

            for i, _id in enumerate(set(doc['ids'] for doc in group['group'])):
                id_lookup[_id] = i

            m = len(id_lookup)
            if m == 1:
                continue

            ratios = np.full((m, m), np.nan)
            ratios_individual = np.full((m, m, k), np.nan)
            table = np.full((m, m), np.nan)
            np.fill_diagonal(table, 1.)

            feature_analysis = dict()
            cached_features = []
            all_features = []
            for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
                compared = compare_pair(pair)
                features = compared['features']

            print(group_id)
            # Won't merge low-objective clusters
            p = predict()
            cluster_labels = custom_cluster_alg(new_table, epsilon=1e-10) # Merge more (if splitting)
