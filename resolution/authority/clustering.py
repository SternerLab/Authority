import itertools
from math import prod
from functools import reduce
from rich.pretty import pprint
from rich import print
import numpy as np

from ..utils import *

def objective(u, v, elements, probs, eps=1e-16):
    U, V = elements[u], elements[v]
    assert len(U) > 0 and len(V) > 0, 'Should not calculate objective for 0-len clusters'
    for i, j in itertools.product(U, V):
        i, j = min(i, j), max(i, j)
        obj = (probs[i, j] / (1 - probs[i, j] + eps)) / ((len(U) * len(V)))
        yield obj

def merge(labels, elements, objectives, probs, u, v, c):
    # Cluster v is being merged
    # print(f'merge {u} {v}')
    for k, l in enumerate(labels):
        if l == v:
            labels[k] = u # Don't make contiguous, just merge them
    elements[u].extend(elements.pop(v))
    objectives[v, :] = np.nan
    objectives[:, v] = np.nan
    for o in elements:
        if o != u:
            i, j = min(u, o), max(u, o)
            objectives[i, j] = prod(objective(u, o, elements, probs))

def cluster(probs, epsilon=1e-8):
    c, _     = probs.shape
    labels   = np.arange(c)
    elements = {i : [labels[i]] for i in range(c)}
    objectives = np.full((c, c), np.nan)
    # Only process all possible pairs before the first iteration.
    # Afterwards, just update the objectives matrix.
    for u, v in itertools.combinations(np.arange(c), r=2): # All cluster pairs
        if u != v:
            objectives[u, v] = prod(objective(u, v, elements, probs))
    prev_best = -float('inf')
    for _ in range(c - 1): # Upper bound on possible merges
        # Calculate the objective and argmax of clusters
        u, v = np.unravel_index(np.nanargmin(objectives), objectives.shape)
        best = objectives[u, v]
        if best < epsilon or (u == v and u == 0): # If below eps or all merged
            break
        prev_best = best
        # Merge clusters u and v. u < v is true by itertools.combinations
        merge(labels, elements, objectives, probs, u, v, c)
        c -= 1
    # Make the labels contiguous, efficiently!
    unique_values, indices = np.unique(labels, return_inverse=True)
    return indices
