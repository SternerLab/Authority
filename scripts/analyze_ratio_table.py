from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle

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

from .inference import get_r_table_data

def run():
    client = MongoClient('localhost', 27017)

    r_table        = client.r_table.r_table
    xi_ratios, interpolated = get_r_table_data(r_table)
    pprint(interpolated)
    pprint(xi_ratios)
    print(interpolated.shape)

    # fig = sns.heatmap(probs).get_figure()
    # fig.savefig(f'plots/{prob_key}.png')
    # plt.show()

    # jstor_database = client.jstor_database
    # inferred       = client.inferred
    # inferred_blocks = inferred['block']
    # inferred_blocks.create_index('group_id')

    # articles = jstor_database.articles
    # articles.create_index('title')
    # articles.create_index('authors.key')

    # val            = client.validation
    # bhl            = val.bhl
    # scholar        = val.google_scholar_doi
    # self_citations = val.self_citations

    # pprint(bhl.find_one())
    # pprint(scholar.find_one())
    # pprint(self_citations.find_one())

    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'johnson'}}
    # for cluster in inferred_blocks.find(query):
    #     pprint(cluster['group_id'])
    #     pprint(cluster['cluster_labels'])
    #     pprint(cluster.keys())
    #     for prior_key in ('match_prior', 'prior'):
    #         prior = cluster['prior']
    #         print(f'{prior_key} : {prior:.4%}')
    #     for prob_key in ('original_probs', 'fixed_probs', 'probs'):
    #         probs = pickle.loads(cluster[prob_key])
    #         fig = sns.heatmap(probs).get_figure()
    #         fig.savefig(f'plots/{prob_key}.png')
    #         plt.show()

    # inferred       = client.inferred

    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'johnson'}}
    # try:
    #     ref_key = 'block'
    #     total = lookup[ref_key].count_documents({})
    #     for pair_lookup in track(lookup[ref_key].find(query), total=total,
    #                              description='Clustering first initial last name blocks'):
    #         group_id = pair_lookup['group_id']
    #         group = next(subsets[ref_key].find({'_id' : group_id}))

    #         pair_ids = pair_lookup['pair_ids']
    #         match_prior = estimate_prior(pair_lookup['n'])
    #         id_lookup = dict()

    #         for i, _id in enumerate(set(doc['ids'] for doc in group['group'])):
    #             id_lookup[_id] = i

    #         m = len(id_lookup)
    #         if m == 1:
    #             continue

    #         table = np.full((m, m), np.nan)
    #         np.fill_diagonal(table, 1.)

    #         cached_features = []
    #         for pair in pairs[ref_key].find({'_id' : {'$in' : pair_ids}}):
    #             compared = compare_pair(pair, articles)
    #             features = compared['features']
    #             p = infer_from_feature(features, interpolated, xi_ratios, match_prior)
    #             i, j = [id_lookup[doc['ids']] for doc in pair['pair']]
    #             i, j = min(i, j), max(i, j)
    #             cached_features.append((i, j, features))
    #             table[i, j] = p

    #         fixed_table = fix_triplet_violations(table)
    #         new_prior   = (np.sum(np.where(fixed_table > 0.5, 1., 0.)) /
    #                        np.sum(np.where(np.isnan(fixed_table), 0., 1.)))

    #         new_table = np.full((m, m), np.nan)
    #         np.fill_diagonal(new_table, 1.)
    #         for i, j, feature in cached_features:
    #             p = infer_from_feature(features, interpolated, xi_ratios, new_prior)
    #             new_table[i, j] = p

    #         print(group_id)
    #         cluster_labels = custom_cluster_alg(new_table)
    #         print('custom', cluster_labels)
    #         binary_probs          = Binary(pickle.dumps(new_table), subtype=128)
    #         fixed_probs_binary    = Binary(pickle.dumps(fixed_table), subtype=128)
    #         original_probs_binary = Binary(pickle.dumps(table), subtype=128)

    #         inferred[ref_key].insert_one(dict(
    #             cluster_labels={str(k) : int(cluster_labels[i])
    #                             for k, i in id_lookup.items()},
    #             probs=binary_probs, prior=new_prior,
    #             fixed_probs=fixed_probs_binary,
    #             original_probs=original_probs_binary,
    #             match_prior=match_prior,
    #             group_id=group_id))
    # except KeyboardInterrupt:
    #     pass



