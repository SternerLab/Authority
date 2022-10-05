from rich.pretty import pprint
from rich.progress import track
from rich import print
import scipy
import numpy as np
import itertools
from collections import namedtuple
import seaborn as sns
import matplotlib.pyplot as plt

from .compute_ratio import *
from .clustering import merge

Triplet = namedtuple('Triplet', ['ij', 'jk', 'ik'])
def trip(table, i, j, k):
    return Triplet(table[i, j], table[j, k], table[i, k])

def inv_var(p, eps=1e-8):
    return 1 / (p * (1 - p) + eps)

Triplet.inv = lambda t : Triplet(inv_var(t.ij), inv_var(t.jk), inv_var(t.ik))

def violation(p, delta=0.05):
    ''' Triplet violation condition, 2009 paper, page 12'''
    return p.ij + p.jk - 1 > p.ik + delta

Triplet.violation = violation

def correct(t, eps=1e-8):
    ''' Closed form solution given in 2009 paper, page 13'''
    w    = t.inv()
    den  = w.ij*w.ik + w.ik*w.jk + w.ij*w.jk + eps
    q_ij = (w.ij*(w.jk + w.ik)*t.ij + w.jk*w.ik*(1 + t.ik - t.jk))/den
    q_jk = (w.jk*(w.ij + w.ik)*t.jk + w.ij*w.ik*(1 + t.ik - t.ij))/den
    q_ik = q_ij + q_jk - 1
    return Triplet(*np.maximum(np.minimum((q_ij, q_jk, q_ik), 0.), 1.))

Triplet.correct = correct

def connected_components(table):
    ''' Yield groups of triplets in the table which form connected components '''
    m, m = table.shape
    components = np.arange(m) # Effectively cluster labels
    n_components = m
    for i, j in itertools.combinations(np.arange(m), r=2): # Upper triangle
        if table[i, j] > 0.5:
            # Merge i and j from u, v -> u
            u, v = components[i], components[j]
            if u != v: # Check that merge is unique and needed
                u, v = min(u, v), max(u, v) # u < v
                for k in range(m): # merge loop
                    if components[k] == v:
                        components[k] = u
                n_components -= 1
    print(f'Connected components found {n_components} components')
    for c in range(n_components): # Yield a generator of triplets for each component
        component = []
        for k in range(m):
            if components[k] == c:
                component.append(k)
        print(c, component)
        yield itertools.combinations(component, r=3) # Triplets in one component

def fix_triplet_violations_step(table, eps=1e-6):
    ''' A single step to fix triplet violations in a probability table '''
    working = np.zeros_like(table)
    base    = np.zeros_like(table)
    m, m = table.shape
    violations = 0
    # for i, j, k in itertools.combinations(np.arange(m), r=3):
    for component in connected_components(table):
        for i, j, k in component:
            t = trip(table, i, j, k)
            assert t.ij < 1. + eps, f'Probability violation in input ij: {t.ij}'
            assert t.jk < 1. + eps, f'Probability violation in input jk: {t.jk}'
            assert t.ik < 1. + eps, f'Probability violation in input ik: {t.ik}'
            if t.violation():
                violations += 1

                q = t.correct()
                assert q.ij < 1. + eps, f'Probability violation in analytic ij: {q.ij}'
                assert q.jk < 1. + eps, f'Probability violation in analytic jk: {q.jk}'
                assert q.ik < 1. + eps, f'Probability violation in analytic ik: {q.ik}'

                working[i, j] += q.ij
                working[j, k] += q.jk
                working[i, k] += q.ik
                base[i, j] += 1.
                base[j, k] += 1.
                base[i, k] += 1.
    # base is 0. where there are no triplet violations:
    assert (working < base + eps).all(), 'Normalization incorrect'
    # Average where we have data
    # It is safe to ignore stability warnings here since we use np.where,
    # And check stability of the upper triangle immediately afterwards
    with np.errstate(invalid='ignore', divide='ignore'):
        updated = np.where(np.isclose(base, 0.), table, working/base) # order matters for warnings
    # Check numerical stability of upper triangle of probability matrix
    for i, j in itertools.combinations(np.arange(m), r=2):
        assert np.isfinite(updated[i, j]), f'Numerical stability violation at i, j = {i, j}: {updated[i, j]}'
    bottom, top = np.nanmin(updated), np.nanmax(updated)
    assert bottom > 0., f'minimum {bottom} violates probability laws'
    assert top <= 1. + eps, f'maximum {top} violates probability laws'
    return updated, violations

def fix_triplet_violations(table, max_iterations=30):
    ''' Fix triplet violations using a closed-form solution,
        section 4 of the 2005 or 2009 papers '''
    for i in range(max_iterations):
        table, violations = fix_triplet_violations_step(table)
        print(f'Iteration {i} of triplet violations: violations = {violations}')
        if violations == 0:
            break
    return table
