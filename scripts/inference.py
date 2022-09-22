from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
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

from authority.algorithm.compare import compare_pair, x_i, x_a
from authority.algorithm.triplet_violations import fix_triplet_violations
from authority.algorithm.clustering import cluster as custom_cluster_alg

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

def estimate_prior(n):
    return 1 / (1 + 10**-1.194 * n**0.7975)

def inference(ratio, prior, eps=1e-10):
    return 1 / (1 + (1 - prior) / (prior * ratio + eps))

def infer_from_feature(features, interpolated, xi_ratios, prior):
    x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
    r_a = interpolated[x3, x4, x5, x6]
    x_i_keys = [f'x{i}' for i in x_i]
    r_is = np.array([xi_ratios.get((k, features[k] if features[k] is not None else 0),
                                    0.) #????? TODO should not happen, is rare.
                                    # Observed for the case x10 = 8,
                                    # which apparently was not observed
                                    # enough to estimate this ratio
                     for k in x_i_keys])
    ratio = np.prod(r_is) * r_a
    return inference(ratio, prior)

def get_r_table_data(r_table):
    xi_ratios = next(r_table.find({'xi_ratios' : {'$exists' : True}}))
    xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}

    interpolated_doc = next(r_table.find(
                            {'interpolated_xa_ratios' : {'$exists' : True}}))
    interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
    return xi_ratios, interpolated

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs
    lookup         = client.reference_sets_group_lookup
    subsets        = client.reference_sets
    inferred       = client.inferred

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table)
    try:
        ref_key = 'block'
        total = lookup[ref_key].count_documents({})
        for pair_lookup in track(lookup[ref_key].find(), total=total):
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

            table = np.full((m, m), np.nan)
            np.fill_diagonal(table, 1.)

            cached_features = []
            for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
                compared = compare_pair(pair, articles)
                features = compared['features']
                p = infer_from_feature(features, interpolated, xi_ratios, match_prior)
                i, j = [id_lookup[doc['ids']] for doc in pair['pair']]
                i, j = min(i, j), max(i, j)
                cached_features.append((i, j, features))
                table[i, j] = p

            fixed_table = fix_triplet_violations(table)
            new_prior   = (np.sum(np.where(fixed_table > 0.5, 1., 0.)) /
                           np.sum(np.where(np.isnan(fixed_table), 0., 1.)))

            new_table = np.full((m, m), np.nan)
            np.fill_diagonal(new_table, 1.)
            for i, j, feature in cached_features:
                p = infer_from_feature(features, interpolated, xi_ratios, new_prior)
                new_table[i, j] = p

            print(group_id)
            cluster_labels = custom_cluster_alg(new_table)
            print('custom', cluster_labels)
            binary_probs   = Binary(pickle.dumps(new_table), subtype=128)
            inferred[ref_key].insert_one(dict(
                cluster_labels={str(k) : int(cluster_labels[i])
                                for k, i in id_lookup.items()},
                probs=binary_probs, prior=new_prior,
                group_id=group_id))
    except KeyboardInterrupt:
        pass



