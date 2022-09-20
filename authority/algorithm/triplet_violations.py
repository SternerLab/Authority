from rich.pretty import pprint
from rich import print
import scipy
import numpy as np

from .compute_ratio import *

def inverse_variance(p):
    return 1 / (p * (1 - p))

def fix_triplet_violations(triplet):
    ''' Fix triplet violations using a closed-form solution,
        section 4 of the 2005 paper '''
    p_ij = triplet[0]
    p_jk = triplet[1]
    p_ik = triplet[2]

    w_ij = 1 / (p_ij * (1-p_ij))
    w_jk = 1 / (p_jk * (1-p_jk))
    w_ik = 1 / (p_ik * (1-p_ik))
    den = w_ij*w_ik + w_ik*w_jk + w_ij*w_jk

    q_ij = (w_ij*(w_jk + w_ik)*p_ij + w_jk*w_ik*(1 + p_ik - p_jk))/den
    q_jk = (w_jk*(w_ij + w_ik)*p_jk + w_ij*w_ik*(1 + p_ik - p_ij))/den
    q_ik = q_ij + q_jk - 1

    return np.array([q_ij, q_jk, q_ik])
