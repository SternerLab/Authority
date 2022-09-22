import itertools
from math import prod
from functools import reduce
import numpy as np

def elements(labels, cluster):
    for i, l in enumerate(labels):
        if l == cluster:
            yield i

def objective(u, v, labels, probs):
    U = np.fromiter(elements(labels, u), int, count=-1) # could store but this is ~fast
    V = np.fromiter(elements(labels, v), int, count=-1)
    for i, j in itertools.product(U, V):
        yield (probs[i, j] / (1 - probs[i, j])) / U.shape[0] * V.shape[0]

def cluster(probs, epsilon=1e-8):
    c, _    = probs.shape
    labels  = np.arange(c)
    for _ in range(c - 1): # Upper bound on possible merges
        # Calculate the objective and argmax of clusters
        best = -float('inf')
        to_merge = None
        for u, v in itertools.combinations(np.arange(c), r=2): # All cluster pairs
            obj = prod(objective(u, v, labels, probs))         # Objective
            if obj > best:
                best = obj
                to_merge = u, v
        u, v = to_merge
        if best < epsilon:
            break
        # Merge clusters u and v
        # u < v is satisfied based on behavior of itertools.combinations!
        for k, l in enumerate(labels):
            if l == v:
                labels[k] = u
            elif l > v:
                labels[k] -= 1
        c -= 1
    return labels

