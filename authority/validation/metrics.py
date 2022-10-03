import pandas as pd
from rich import print
from collections import namedtuple
import numpy as np

# summary = namedtuple('')

# See https://journals.sagepub.com/doi/pdf/10.1177/0165551519888605?casa_token=y1zlBGjQm_4AAAAA:y_JtVhx3ZjIJ3vUic2WLmat14KUv1aTwvmYIcq_ji7kdtAoLT0wREo5dWM25ySaTlpiGVjzeL3D_Ew

def pairwise_metrics():
    tp = 10
    tn = 10
    fp = 10
    fn = 10
    s  = tp + tn + fp + fn
    accuracy                = (tp + tn) / s
    precision = pp = tp / (tp + fp)
    recall    = pr = tp / (tp + fn)
    f1             = (2 * pp * pr) / (pp + pr)
    lumping        = fp / (tp + fp) # Correct? was written as (fp / (tp / fp)) in paper
    splitting      = fn / (tn + fn)
    error          = (fp + fn) / s
    return dict(locals())

def metrics():
    total_authors = 4
    correct_clusters = 3
    total_clusters = 3
    true_clusters = 3
    clusters = [{1, 2}, {3}, {4}]
    reference_clusters = clusters # TODO

    cluster_precision  = cp = correct_clusters / total_clusters
    cluster_recall     = cr = correct_clusters / true_clusters
    cluster_f1              = (2 * cp * cr) / (cp + cr)

    cluster_ratio           = total_clusters / true_clusters

    cluster_purity = 0
    for i in range(total_clusters):
        for j in range(true_clusters):
            correct   = len({k for k in clusters[i] if k in reference_clusters[j]})
            normalize = len(clusters[i])
            cluster_purity += correct ** 2 / normalize
    cluster_purity = cluster_purity / total_authors

    author_purity = 0
    for i in range(true_clusters):
        for j in range(total_clusters):
            correct   = len({k for k in clusters[i] if k in reference_clusters[j]})
            normalize = len(clusters[i])
            author_purity += correct ** 2 / normalize
    author_purity = author_purity / total_authors

    k_measure = np.sqrt(cluster_purity * author_purity)

    contained = lambda s, cs : [c for c in cs if s in c][0]

    b_cubed_precision = 0
    b_cubed_recall    = 0
    for s in range(1, total_authors + 1):
        V = contained(s, clusters)
        T = {si for si in V
             if contained(si, reference_clusters) == contained(s, reference_clusters)}
        ref_precision = len(T)/len(V)
        b_cubed_precision += ref_precision

        C = contained(s, reference_clusters)
        U = {si for si in C
             if contained(si, clusters) == contained(s, clusters)}
        ref_recall    = len(U)/len(C)
        b_cubed_recall += ref_recall

    del V, T, C, U, ref_recall, ref_precision, contained # Don't return these

    b_cubed_precision = bp =  b_cubed_precision / total_authors
    b_cubed_recall    = br =  b_cubed_recall / total_authors
    b_cubed_f1             = (2 * bp * br) / (bp + br)
    return dict(locals())


print(pairwise_metrics())
print(metrics())
