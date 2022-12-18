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

from resolution.authority.inference import *

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
    # ratios_from = 'previous'
    # ratios_from = 'previous'
    ratios_from = 'default'

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table, ratios_from=ratios_from)
    # excluded = {'x7'}
    # excluded = {'x2'}
    # excluded = {'x2', 'x7'}
    excluded = set()
    k = len(x_i) - len(excluded) + 1 # x_i features + 1 for x_a features
    if ratios_from == 'previous':
        k -= 1
    infer_kwargs = dict(excluded=excluded, apply_stability=False, ratios_from=ratios_from)
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
                all_features = dict()
                for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
                    compared = compare_pair(pair)
                    features = compared['features']
                    feature_key = '-'.join(str(p['ids']) for p in pair['pair'])
                    all_features[feature_key] = features
                    feature_key = ' '.join(map(str, features.values()))
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

                inferred[ref_key].insert_one(dict(
                    cluster_labels={str(k) : int(cluster_labels[i])
                                    for k, i in id_lookup.items()},
                    feature_analysis=feature_analysis,
                    features=all_features,
                    prior=new_prior,
                    match_prior=match_prior,
                    group_id=group_id))
                for name, data in [('original',  table),
                                   ('corrected', fixed_table),
                                   ('final',     new_table),
                                   ('ratios',    ratios),
                                   ('ratios_individual', ratios_individual)]:
                    np.savez(f'/workspace/resolution_probs/{group_id}_{name}.npz', data)
    except KeyboardInterrupt:
        pass

# Inference type signature
# block -> cluster labels, aux data
# Inference overall loop
# block generator (inference fn)

