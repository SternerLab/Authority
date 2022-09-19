from rich.pretty import pprint
from rich import print
import scipy
import numpy as np
import itertools

from .compare import limits, x_a

def interpolate(computed_ratios):
    ''' Interpolation, section 2b of the 2005 paper '''

    interpolated = np.zeros(tuple((l + 1 for l in limits.values())))
    profiles = list(computed_ratios.items())
    lower_profile, lower_r = profiles[0]
    upper_profile, upper_r = profiles[-1]

    i = 0
    preceeding = None
    preceeding_r = lower_r
    succeeding = lower_profile
    succeeding_r = lower_r

    for key in itertools.product(*(np.arange(l + 1) for l in limits.values())):
        x3, x4, x5, x6 = key
        if key > succeeding:
            if (i + 1) < len(profiles):
                preceeding, preceeding_r = profiles[i]
                succeeding, succeeding_r = profiles[i + 1]
                i += 1
            else:
                preceeding, preceeding_r = profiles[-1]
                succeeding, succeeding_r = profiles[-1]
        interpolated[x3, x4, x5, x6] = (preceeding_r + succeeding_r) / 2
    return interpolated
