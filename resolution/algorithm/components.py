import numpy as np
import itertools

def connected_components(table):
    ''' Yield groups of triplets in the table which form connected components '''
    m, m = table.shape
    components = np.arange(m) # Effectively cluster labels
    for i, j in itertools.combinations(np.arange(m), r=2): # Upper triangle
        if table[i, j] > 0.5:
            # Merge i and j from u, v -> u
            u, v = components[i], components[j]
            if u != v: # Check that merge is unique and needed
                u, v = min(u, v), max(u, v) # u < v
                for k in range(m): # merge loop
                    if components[k] == v:
                        components[k] = u
    return components

