import numpy as np
from authority.algorithm.triplet_violations import fix_triplet_violations

def run():
    print('Testing triplet violation code')
    # let triplet be [pij pjk pik]
    triplet = np.array([0.1, 0.1, 0.9])
    delta = 0.05
    print(triplet)
    print(triplet[0] + triplet[1], triplet[2] + delta)
    fixed = fix_triplet_violations(triplet)
    print(fixed)

