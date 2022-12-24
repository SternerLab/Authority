from rich.pretty import pprint
from rich.progress import track
from rich import print
from bson.son import SON
from bson.binary import Binary
import itertools
import json
import scipy
import dill as pickle
import numpy as np
from pathlib import Path

import itertools
from dataclasses import dataclass, field
import logging
log = logging.getLogger('rich')

from .compare    import compare_pair, x_i, x_a
from .clustering import cluster as custom_cluster_alg
from ..algorithm.inference import *

@dataclass
class AuthorityInferenceMethod(InferenceMethod):
    # General inference fields
    correct_triplets: bool = field(default=True)
    reestimate: bool       = field(default=True)
    # Authority specific fields
    xi_ratios: dict = None
    interpolated_xa: 'typing.Any' = None # called xa_ratios in Torvik's notation

    # It is required that cluster and pairwise do not share keys
    cluster_params:  dict = field(default_factory=lambda : dict(epsilon=1e-6))
    pairwise_params: dict = field(default_factory=lambda : dict(excluded=None, apply_stability=False,
        clip=True, ratios_from='default'))

    def __post_init__(self):
        super().__post_init__()
        self.xi_ratios, self.interpolated_xa = get_r_table_data(
                self.client.r_table,
                ratios_from=self.pairwise_params['ratios_from'])

    def pairwise_infer(self, pair, n=None, prior=None, clip=True,
                       apply_stability=False, excluded=None,
                       ratios_from='default'):
        if prior is None:
            assert n is not None, 'Must have n to estimate initial prior'
            prior = estimate_prior(n)
        assert prior is not None, 'prior must be provided for each block'
        compared = compare_pair(pair)
        features = compared['features']

        if excluded is None:
            excluded = set()
        x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
        match ratios_from:
            case 'previous':
                r_a = self.interpolated_xa.get((features['x10'] + 1, x3, x4, x5, x6), 1.0)
                excluded.add('x10')
            case _:
                r_a = self.interpolated_xa[x3, x4, x5, x6]
        x_i_keys = [f'x{i}' for i in x_i]
        r_is = np.array([self.xi_ratios.get((k, features[k]), 1.0) # Sensible default value
                         for k in x_i_keys if k not in excluded] + [r_a])
        if not (r_is > 0.).all():
            log.warning(f'Ratios are not greater than 0: {r_is}')
            r_is = np.maximum(r_is, 0.)
        if clip:
            r_is = np.minimum(r_is, 10.)
        if apply_stability:
            epsilon = 1e-3
            r_is = np.where(r_is > 1.0, np.log10(r_is) / np.log10(42), r_is + epsilon)
        ratio = np.prod(r_is) # Could replace with np.sum() potentially for stability
        return ratio_inference(ratio, prior)

    def pair_cluster_method(self, table, **cluster_params):
        return custom_cluster_alg(table, **cluster_params)

def estimate_prior(n):
    return 1 / (1 + 10**-1.194 * n**0.7975)

def ratio_inference(ratio, prior, eps=1e-10):
    result = 1 / (1 + (1 - prior) / (prior * ratio + eps))
    return result

def parse_previous_ratios():
    x_i_keys = [f'x{i}' for i in x_i]
    xi_ratios = dict()
    for x_i_key in x_i_keys:
        path = Path(f'previous_data/r_{x_i_key}.json')
        r_slice = json.loads(path.read_text())
        xi_ratios.update({(x_i_key, int(v)) : r for v, r in r_slice.items()})
    path = Path(f'previous_data/r_final.json')
    r_interpolated = json.loads(path.read_text())
    interpolated = {tuple(int(v.strip()) for v in s.replace('[', '').replace(']', '').split(',')) :
                    r for s, r in r_interpolated.items()} # Ah yes..
    return xi_ratios, interpolated

def get_r_table_data(r_table, ratios_from='default'):
    match ratios_from:
        case 'torvik_reported':
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
            # Yes, this is copied :(
            interpolated_doc = next(r_table.torvik.find({'interpolated_xa_ratios' : {'$exists' : True}}))
            interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
        case 'previous':
            xi_ratios, interpolated = parse_previous_ratios()
        case key:
            # Fetch estimated xi_ratios
            xi_ratios = r_table[key].find_one({'xi_ratios' : {'$exists' : True}})
            if xi_ratios is None:
                print(f'Could not find ratio table for {key}, but found:')
                for doc in r_table[key].find():
                    print(doc)
            xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}
            interpolated_doc = r_table[key].find_one({'interpolated_xa_ratios' : {'$exists' : True}})
            if interpolated_doc is None:
                print(f'Could not find interpolated ratios for key {key}')
                for doc in r_table[key].find():
                    print(doc)
            interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])

    return xi_ratios, interpolated
