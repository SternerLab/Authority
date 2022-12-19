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
from pathlib import Path

import itertools

from copy import deepcopy
from dataclasses import dataclass

from .triplet_violations import fix_triplet_violations

@dataclass
class InferenceMethod:
    client: 'typing.Any'
    name: str
    direct: bool           = False  # If the inference method gives clusters directly
    correct_triplets: bool = False # If analytic triplet correction should be applied
    reestimate: bool       = False # If the predictions should be re-estimated after triplets
    datapath: 'typing.Any' = Path('/workspace/resolution')
    pairwise_params: 'typing.Any'  = None
    cluster_params:  'typing.Any'  = None
    hyperparameters: 'typing.Any'  = None

    def __post_init__(self):
        assert len(set(self.cluster_params.keys()) & set(self.pairwise_params.keys())) == 0, 'Cannot share keys between cluster and pairwise'
        if self.hyperparameters is not None:
            for k, v in self.hyperparameters:
                if k in self.cluster_params:
                    self.cluster_params[k] = v
                elif k in self.pairwise_params:
                    self.pairwise_params[k] = v


    def infer_clusters(self, pair_docs, group, id_lookup, **local_overrides):
        ''' Return cluster labels and auxillary data '''
        local_pairwise_params = deepcopy(self.pairwise_params)
        local_pairwise_params.update(**local_overrides)
        if direct:
            return self.infer_direct(pair_docs, group, id_lookup, **self.cluster_params)
        else:
            table = self.fill_table(pair_docs, group, id_lookup, **local_pairwise_params)
            if correct_triplets:
                table = fix_triplet_violations(table)
                if reestimate:
                    new_prior = (np.sum(np.where(table > 0.5, 1., 0.)) /
                                 np.sum(np.where(np.isnan(table), 0., 1.)))
                    local_pairwise_params['prior'] = new_prior
                    table = self.fill_table(pair_docs, group, id_lookup, **local_pairwise_params)
                    table = fix_triplet_violations(table)
            cluster_labels = self.cluster_method(new_table, **self.cluster_params)
            return cluster_labels

    def infer_direct(self, pair_docs, group, id_lookup, **kwargs):
        raise NotImplementedError

    def pairwise_infer(self, pair, **pairwise_params): # -> cond_prob
        raise NotImplementedError

    def cluster_method(self, table, **cluster_params):
        ''' Cluster from pairwise probabilities '''
        raise NotImplementedError

    def fill_table(self, pair_docs, group, id_lookup, **pairwise_params):
        m = len(id_lookup)
        table = np.full((m, m), np.nan)
        np.fill_diagonal(table, 1.)
        for pair in pair_docs:
            i, j = (id_lookup[doc['ids']] for doc in pair['pair'])
            i, j = min(i, j), max(i, j)
            p = self.pairwise_infer(pair, **pairwise_params)
            assert p >= 0. and p <= 1., f'Probability estimate {p} for features {features} violates probability laws, using ratio {r} and prior {match_prior}'
            table[i, j] = p
        for i, j in itertools.combinations(range(m), 2):
            i, j = min(i, j), max(i, j)
            assert not table[i, j].isnan(), f'Probability table not filled at {(i, j)}'
        return table

def infer_with(*args, **kwargs):
    ''' Separate function to create a generator'''
    description = f'{method.name} inference on {total} docs'
    for pair_lookup in track(lookup.find(query, session=session,
                             no_cursor_timeout=True), total=total,
                             description=description):
        group_id = pair_lookup['group_id']
        group    = group_cache[str(group_id)]
        pair_ids = pair_lookup['pair_ids']

        id_lookup = dict()
        for i, _id in enumerate(set(doc['ids'] for doc in group['group'])):
            id_lookup[_id] = i

        m = len(id_lookup)
        if m == 1:  # No point in classifying a single document
            continue

        pair_docs = [pair for pair in pairs.find({'_id' : {'$in' : pair_ids}})]
        clusters, aux = method.infer(pair_docs, group, id_lookup)
        cluster_labels={str(k) : int(cluster_labels[i])
                        for k, i in id_lookup.items()},
        yield dict(cluster_labels=cluster_labels, group_id=group_id, **aux)

def save_aux_data(group_id, aux):
    to_pop = []
    for k, v in aux.items():
        if isinstance(v, np.array):
            to_pop.append(k)
            np.savez(self.datapath / f'{group_id}_{name}.npz', v)
    for k in to_pop:
        aux.pop(k)

def inference(client, inference_methods, query=None, ref_key='first_initial_last_name'):
    if query is None:
        query = {}

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs[ref_key]
    lookup         = client.reference_sets_group_lookup[ref_key]
    subsets        = client.reference_sets[ref_key]
    inferred       = client.inferred

    try:
        with client.start_session(causal_consistency=True) as session:
            group_cache = dict()
            for doc in subsets.find():
                group_cache[str(doc['_id'])] = doc

            total = lookup.count_documents(query)
            for method in methods:
                method_cursor = infer_with(method, lookup, group_cache, pairs, session)
                inferred[method.name].insert_many(method_cursor)
    except KeyboardInterrupt:
        print(f'Interrupted inference, stopping gracefully...', flush=True)