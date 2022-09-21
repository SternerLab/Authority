from rich.pretty import pprint
from rich import print
import scipy
import numpy as np
import itertools

from .compare import limits, x_a

def preceeding_max(profiles, key):
    return np.max(np.array([r for t, r in profiles if sum(t) < sum(key)]))

def succeeding_min(profiles, key):
    return np.min(np.array([r for t, r in profiles if sum(t) > sum(key)]))

def interpolate(computed_ratios):
    ''' Interpolation, section 2b of the 2005 paper '''

    interpolated = np.zeros(tuple((l + 1 for l in limits.values())))
    profiles = list(computed_ratios.items())
    profile_lookup = {t : r for t, r in profiles}

    for key in itertools.product(*(np.arange(l + 1) for l in limits.values())):
        x3, x4, x5, x6 = key
        if key not in profile_lookup:
            preceeding_r = preceeding_max(profiles, key)
            succeeding_r = succeeding_min(profiles, key)
            interpolated[x3, x4, x5, x6] = (preceeding_r + succeeding_r) / 2
        else:
            interpolated[x3, x4, x5, x6] = profile_lookup[key]
    return interpolated