import itertools
from ..utils import *

def merge(aid, cid, resolved):
    ''' Somewhat ugly because it accounts for edge cases.. '''
    # M is a boolean denoting if an entry has been merged already
    (prev, m), (prev_c, m_c) = resolved[aid], resolved[cid]
    u, v = min(prev, prev_c), max(prev, prev_c)
    for k, (l, m_k) in resolved.items():
        if l == v:
            resolved[k] = (u, True)
        elif l > v:
            resolved[k] = (resolved[k][0] - 1, m_k)

def batched(generator, batch_size=32):
    while True:
        batch = list(itertools.islice(generator, batch_size))
        if not batch:
            break
        else:
            yield batch

# I think I've accidentally written boilerplate like this multiple times,
# so here is a definitive one that can replace the others..
def pairs_to_cluster_labels(id_pairs):
    count = 0
    labels = dict()
    for a, b in id_pairs:
        if a in labels:
            if b in labels:
                if labels[a] != labels[b]:
                    merge_labels(a, b, labels)
            else:
                labels[b] = labels[a]
        else:
            if b in labels:
                labels[a] = labels[b]
            else:
                labels[a] = labels[b] = count
                count += 1
    return labels
