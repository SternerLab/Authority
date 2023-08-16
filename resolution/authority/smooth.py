from rich.pretty import pprint
from rich import print
import scipy
import numpy as np

from .compute_ratio import *

def smooth(computed_ratios):
    ''' Smoothing, section 2a of the 2005 paper '''
    l  = len(computed_ratios)
    x  = np.zeros(l)
    ws = np.zeros(l)
    rs = np.zeros(l)

    for i, (k, (r, w)) in enumerate(computed_ratios.items()):
        ws[i] = w
        rs[i] = r
        x[i]  = r  # This modifies the starting point of SLSQP

    def objective(x):
        return ws @ (rs - x)**2

    def constraint(x):
        bound = np.concatenate((x[1:], x[-1:]), axis=-1)
        # since this needs to be positive, it constrains to monotonicity
        return bound - x

    print(f'Starting: ', x)
    rh = scipy.optimize.minimize(objective, x, method='slsqp',
            constraints=[dict(type='ineq', fun=constraint)],
            bounds=scipy.optimize.Bounds(lb=0.0))['x']
    print('Smoothing solution: ', rh)

    for i, k in enumerate(computed_ratios):
        computed_ratios[k] = rh[i]
        assert rh[i] >= 0., f'ratios should ALWAYS be positive, but got {rh[i]}'
    return computed_ratios
