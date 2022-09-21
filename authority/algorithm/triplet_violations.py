from rich.pretty import pprint
from rich import print
import scipy
import numpy as np
import itertools

from .compute_ratio import *

def inv_var(p):
    return 1 / (p * (1 - p))

def triplet_violation(table, i, j, k, delta=0.05):
    ''' Triplet violation condition, 2009 paper, page 12'''
    p_ij = table[i, j]
    p_jk = table[j, k]
    p_ik = table[i, k]
    return p_ij + p_jk - 1 > p_ik + delta

def solve_triplet_violation(table, i, j, k):
    ''' Closed form solution given in 2009 paper, page 13'''
    p_ij = table[i, j]
    p_jk = table[j, k]
    p_ik = table[i, k]

    w_ij = inv_var(p_ij)
    w_jk = inv_var(p_jk)
    w_ik = inv_var(p_ik)

    den = w_ij*w_ik + w_ik*w_jk + w_ij*w_jk

    q_ij = (w_ij*(w_jk + w_ik)*p_ij + w_jk*w_ik*(1 + p_ik - p_jk))/den
    q_jk = (w_jk*(w_ij + w_ik)*p_jk + w_ij*w_ik*(1 + p_ik - p_ij))/den
    q_ik = q_ij + q_jk - 1

    return q_ij, q_jk, q_ik

def fix_triplet_violations(table):
    ''' Fix triplet violations using a closed-form solution,
        section 4 of the 2005 or 2009 papers '''
    working = np.zeros_like(table)
    base    = np.zeros_like(table)
    m, m = table.shape
    for i, j, k in itertools.combinations(np.arange(m), r=3):
        if triplet_violation(table, i, j, k):
            q_ij, q_jk, q_ik = solve_triplet_violation(table, i, j, k)
            working[i, j] += q_ij
            working[j, k] += q_jk
            working[i, k] += q_ik
            base[i, j] += 1.
            base[j, k] += 1.
            base[i, k] += 1.
    averaged = working / base
    # averaged will be nan where base was 0.,
    # which is where there were no triplet violations
    # and thus should be the original table values
    updated = np.where(np.isnan(averaged), table, averaged)
    return updated