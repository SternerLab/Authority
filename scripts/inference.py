from pymongo import MongoClient
import pymongo
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
    result = 1 / (1 + (1 - prior) / (prior * ratio + eps))
    # print(f'inference: {ratio}, {prior}, {result}')
    return result

def infer_from_feature(features, interpolated, xi_ratios, prior, apply_stability=False, excluded=None):
    x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
    r_a = interpolated[x3, x4, x5, x6]
    x_i_keys = [f'x{i}' for i in x_i]
    # x1, x2, x7, x10
    if excluded is None:
        excluded = set()
    # if apply_stability:
    #     epsilon = 1e-3
    #     r_a = np.where(r_a > 1.0, np.log10(r_a) / np.log10(42), r_a + epsilon)
    r_is = np.array([xi_ratios.get((k, features[k] if features[k] is not None else 0), 0)
                     for k in x_i_keys if k not in excluded] + [r_a])
    r_is = np.abs(r_is) # just in case?
    # r_is = np.maximum(r_is, 1e-4)
    # r_is = np.maximum(r_is, 1e-2)
    # print(r_is)
    # oh boy :)
    # r_is = np.minimum(np.maximum(r_is, 1e-2), 10.)
    # r_is += 1e-1
    # r_is = np.maximum(r_is, 1e-2)
    # print(r_is)

    # if apply_stability:
    #     epsilon = 1e-1
    #     r_is = np.where(r_is > 1.0, np.log10(r_is), r_is + epsilon) # :)
    #     # r_is = np.where(r_is > 1.0, np.log(r_is) / np.log(6.283185307179586476925286766559005768394338798750218857621951), r_is + epsilon) # :)
    # r_is = r_is[-1:]
    # print(r_is)

    ratio = np.prod(r_is) # Could replace with np.sum() potentially
    return inference(ratio, prior), ratio, r_is

def get_r_table_data(r_table, use_torvik_ratios=False):
    if use_torvik_ratios:
        xi_ratios = {('x1', 0) : 0.01343,
                     ('x1', 1) : 0.09295,
                     ('x1', 2) : 2.2058,
                     ('x1', 3) : 14.5140,
                     ('x2', 0) : 0.9978,
                     ('x2', 1) : 242.16,
                     ('x7', 0) : 0.001974,
                     ('x7', 1) : 0.08700,
                     ('x7', 2) : 1.5211,
                     ('x7', 3) : 3.3532 }
    else:
        # Fetch estimated xi_ratios
        xi_ratios = next(r_table.find({'xi_ratios' : {'$exists' : True}}))
        xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}

    interpolated_doc = next(r_table.find({'interpolated_xa_ratios' : {'$exists' : True}}))
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
    inferred.drop_collection('first_initial_last_name')
    print(f'Possible collections:')
    for collection in lookup.list_collection_names():
        print('    ', collection)

    # query = {'group_id' : {'first_initial' : 'b', 'last' : 'johnson'}}
    # query = {'group_id' : {'first_initial' : 'a'}}
    # query = {'group_id' : {'first_initial' : 'b', 'last' : 'johnson'}}
    query = {}

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table, use_torvik_ratios=False)
    # excluded = {'x7'}
    # excluded = {'x2'}
    # excluded = {'x2', 'x7'}
    excluded = set()
    k = len(x_i) - len(excluded) + 1 # x_i features + 1 for x_a features
    infer_kwargs = dict(excluded=excluded, apply_stability=False)
    try:
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
                for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
                    compared = compare_pair(pair)
                    features = compared['features']
                    feature_key = ' '.join(map(str, features.values()))
                    # print(features, feature_key)
                    p, r, rs = infer_from_feature(features, interpolated, xi_ratios, match_prior, **infer_kwargs)
                    rs_binary = Binary(pickle.dumps(rs), subtype=128)
                    if feature_key not in feature_analysis:
                        feature_analysis[feature_key] = p, r, rs_binary, 1
                    else:
                        _, _, _, c = feature_analysis[feature_key]
                        feature_analysis[feature_key] = p, r, rs_binary, c + 1
                    assert r >= 0., f'Ratio {r} violates >0 constraint'
                    assert p >= 0. and p <= 1., f'Probability estimate {p} for features {features} violates probability laws, using ratio {r} and prior {match_prior}'
                    i, j = [id_lookup[doc['ids']] for doc in pair['pair']]
                    i, j = min(i, j), max(i, j)
                    cached_features.append((i, j, features))
                    table[i, j] = p
                    ratios[i, j] = r
                    ratios_individual[i, j] = rs

                # Disable triplet violation correction, prior estimation, and recalculation
                # Set tables and priors to unchanged values for consistency
                fixed_table = fix_triplet_violations(table)
                new_prior   = (np.sum(np.where(fixed_table > 0.5, 1., 0.)) /
                               np.sum(np.where(np.isnan(fixed_table), 0., 1.)))
                new_table = np.full((m, m), np.nan)
                np.fill_diagonal(new_table, 1.)
                for i, j, features in cached_features: #!!!
                    p, r, rs = infer_from_feature(features, interpolated, xi_ratios, new_prior, **infer_kwargs)
                    assert r >= 0., f'Ratio {r} violates >0 constraint'
                    assert p >= 0. and p <= 1., f'Probability estimate {p} for features {features} violates probability laws, using ratio {r} and prior {match_prior}'
                    new_table[i, j] = p

                print(group_id)
                # Won't merge low-objective clusters
                cluster_labels = custom_cluster_alg(new_table, epsilon=1e-10) # Merge more (if splitting)

                print('custom', cluster_labels)
                binary_probs             = Binary(pickle.dumps(new_table), subtype=128)
                fixed_probs_binary       = Binary(pickle.dumps(fixed_table), subtype=128)
                original_probs_binary    = Binary(pickle.dumps(table), subtype=128)
                ratios_binary            = Binary(pickle.dumps(ratios), subtype=128)
                ratios_individual_binary = Binary(pickle.dumps(ratios_individual), subtype=128)

                try:
                    inferred[ref_key].insert_one(dict(
                        cluster_labels={str(k) : int(cluster_labels[i])
                                        for k, i in id_lookup.items()},
                        feature_analysis=feature_analysis,
                        probs=binary_probs,
                        fixed_probs=fixed_probs_binary,
                        original_probs=original_probs_binary,
                        ratios=ratios_binary,
                        ratios_individual=ratios_individual_binary,
                        prior=new_prior,
                        match_prior=match_prior,
                        group_id=group_id))
                except pymongo.errors.DocumentTooLarge:
                    inferred[ref_key].insert_one(dict(
                        cluster_labels={str(k) : int(cluster_labels[i])
                                        for k, i in id_lookup.items()},
                        feature_analysis=feature_analysis,
                        probs=binary_probs, prior=new_prior,
                        ratios=ratios_binary,
                        match_prior=match_prior, group_id=group_id))
    except KeyboardInterrupt:
        pass



