from rich.pretty import pprint
from rich.progress import track
from rich import print
import scipy
import numpy as np
import itertools
from collections import namedtuple

from .compute_ratio import *

Triplet = namedtuple('Triplet', ['ij', 'jk', 'ik'])
def trip(table, i, j, k):
    return Triplet(table[i, j], table[j, k], table[i, k])

def inv_var(p):
    return 1 / (p * (1 - p))

Triplet.inv = lambda t : Triplet(inv_var(t.ij), inv_var(t.jk), inv_var(t.ik))

def violation(p, delta=0.05):
    ''' Triplet violation condition, 2009 paper, page 12'''
    return p.ij + p.jk - 1 > p.ik + delta

Triplet.violation = violation

def correct(t):
    ''' Closed form solution given in 2009 paper, page 13'''
    w    = t.inv()
    den  = w.ij*w.ik + w.ik*w.jk + w.ij*w.jk
    q_ij = (w.ij*(w.jk + w.ik)*t.ij + w.jk*w.ik*(1 + t.ik - p.jk))/den
    q_jk = (w.jk*(w.ij + w.ik)*t.jk + w.ij*w.ik*(1 + t.ik - p.ij))/den
    q_ik = q_ij + q_jk - 1
    return Triplet(q_ij, q_jk, q_ik)

Triplet.correct = correct

def fix_triplet_violations_step(table, epsilon=1e-1): # This epsilon is VERY high
    ''' A single step to fix triplet violations in a probability table '''
    working = np.zeros_like(table)
    base    = np.zeros_like(table)
    m, m = table.shape
    violations = 0
    for i, j, k in itertools.combinations(np.arange(m), r=3):
        t = trip(table, i, j, k)
        if t.violation():
            violations += 1

            q = t.correct()

            working[i, j] += q.ij
            working[j, k] += q.jk
            working[i, k] += q.ik
            base[i, j] += 1.
            base[j, k] += 1.
            base[i, k] += 1.
    # base is 0. where there are no triplet violations:
    print('working', working)
    print('base', base)
    updated = np.where(base > 0., working/base, table)    # Average where we have data
    for i, j in itertools.combinations(np.arange(m), r=2):
        assert not np.isnan(updated[i, j]), f'Numerical stability violation at i, j = {i, j}: {updated[i, j]}'
    # Would not be needed if the above assertion holds, which we want it to!
    # updated = np.where(np.isnan(updated), table, updated) # Don't allow nans
    print('updated', updated)
    print('Bounds: ')
    bottom, top = np.nanmin(updated), np.nanmax(updated)
    assert bottom > 0.
    assert top <= 1. + epsilon, f'maximum {top} violates probability laws'
    print(bottom, top)
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
