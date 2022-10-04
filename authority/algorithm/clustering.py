import itertools
from math import prod
from functools import reduce
from rich.pretty import pprint
from rich import print
import numpy as np

def objective(u, v, elements, probs):
    U, V = elements[u], elements[v]
    for i, j in itertools.product(U, V):
        i, j = min(i, j), max(i, j)
        yield (probs[i, j] / (1 - probs[i, j])) / (len(U) * len(V))

def cluster(probs, stop='threshold', epsilon=1e-8):
    c, _     = probs.shape
    labels   = np.arange(c)
    elements = {i : [labels[i]] for i in range(c)}
    prev_best = -float('inf')
    for _ in range(c - 1): # Upper bound on possible merges
        # Calculate the objective and argmax of clusters
        best = -float('inf')
        to_merge = None
        for u, v in itertools.combinations(np.arange(c), r=2): # All cluster pairs
            obj = prod(objective(u, v, elements, probs))       # Objective
            if obj > best:
                best = obj
                to_merge = u, v
        u, v = to_merge
        if stop == 'compare_threshold':
            print('checking stop condition: best=', best, 'prev_best=', prev_best)
            print('checking epsilon: ', best - prev_best, (best - prev_best) < epsilon)
            if (best - prev_best) < epsilon:
                break
        elif stop == 'threshold':
            print('checking stop condition', best, epsilon)
            if best < epsilon:
                break
        else:
            print(f'Unknown stopping condition {stop}')
        prev_best = best
        # Merge clusters u and v
        # u < v is satisfied based on behavior of itertools.combinations!
        elements[u].extend(elements.pop(v))
        for i in range(v + 1, c):
            elements[i - 1] = elements.pop(i)
        for k, l in enumerate(labels):
            if l == v:
                labels[k] = u
            elif l > v:
                labels[k] -= 1
        c -= 1
    return labels

