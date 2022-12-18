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

from .compare import compare_pair, x_i, x_a
from .triplet_violations import fix_triplet_violations
from .clustering import cluster as custom_cluster_alg

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

def estimate_prior(n):
    return 1 / (1 + 10**-1.194 * n**0.7975)

def inference(ratio, prior, eps=1e-10):
    result = 1 / (1 + (1 - prior) / (prior * ratio + eps))
    # print(f'inference: {ratio}, {prior}, {result}')
    return result

def infer_from_feature(features, interpolated, xi_ratios, prior, apply_stability=False, excluded=None,
                       ratios_from='default'):
    if excluded is None:
        excluded = set()
    x3, x4, x5, x6 = (features[f'x{i}'] for i in x_a)
    if ratios_from == 'default':
        r_a = interpolated[x3, x4, x5, x6]
    else:
        r_a = interpolated.get((features['x10'] + 1, x3, x4, x5, x6), 1.0)
        excluded.add('x10')
    x_i_keys = [f'x{i}' for i in x_i]
    r_is = np.array([xi_ratios.get((k, features[k] if features[k] is not None else 0), 0)
                     for k in x_i_keys if k not in excluded] + [r_a])
    assert (r_is > 0.).all()
    r_is = np.abs(r_is) # just in case?
    r_is = np.minimum(r_is, 10.) # Should ablate
    # r_is = np.where(r_is > 1.0, np.log10(r_is) / np.log10(42), r_is + epsilon)
    ratio = np.prod(r_is) # Could replace with np.sum() potentially
    return inference(ratio, prior), ratio, r_is

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
        case 'torvik':
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
            interpolated_doc = next(r_table.find({'interpolated_xa_ratios' : {'$exists' : True}}))
            interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
        case 'default':
            # Fetch estimated xi_ratios
            xi_ratios = next(r_table.find({'xi_ratios' : {'$exists' : True}}))
            xi_ratios = {(k, v) : l for k, v, l in xi_ratios['xi_ratios']}
            interpolated_doc = next(r_table.find({'interpolated_xa_ratios' : {'$exists' : True}}))
            interpolated = pickle.loads(interpolated_doc['interpolated_xa_ratios'])
        case 'previous':
            xi_ratios, interpolated = parse_previous_ratios()

    return xi_ratios, interpolated

