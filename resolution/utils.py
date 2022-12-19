def merge_labels(a, b, labels):
    la, lb = labels[a], labels[b]
    u, v = min(la, lb), max(la, lb)
    for k, l in labels.items():
        if l == v:
            resolved[k] = (u)
        elif l > v:
            resolved[k] = labels[k] - 1

def make_contiguous(cluster):
    if len(cluster) == 0:
        return cluster
    l = max(cluster.values()) + 1
    not_dropped = set(cluster.values())
    dropped = [c for c in range(l) if c not in not_dropped]
    update_label = lambda v : v - sum(1 for d in dropped if d < v)
    contiguous = {k : update_label(v) for k, v in cluster.items()}
    return contiguous
