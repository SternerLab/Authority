import pandas as pd
from rich import print
from rich.pretty import pprint
from collections import namedtuple
import numpy as np
import itertools

# See https://journals.sagepub.com/doi/pdf/10.1177/0165551519888605?casa_token=y1zlBGjQm_4AAAAA:y_JtVhx3ZjIJ3vUic2WLmat14KUv1aTwvmYIcq_ji7kdtAoLT0wREo5dWM25ySaTlpiGVjzeL3D_Ew

class IncompleteValidation(Exception):
    pass

def pairwise_metrics(clusters, reference_clusters):
    tp, tn, fp, fn = (np.float32(v) for v in unpack(clusters, reference_clusters))
    with np.errstate(divide='ignore', invalid='ignore'):
        s              = tp + tn + fp + fn
        accuracy       = (tp + tn) / s
        precision = pp = tp / (tp + fp)
        recall    = pr = tp / (tp + fn)
        f1             = (2 * pp * pr) / (pp + pr)
        lumping        = fp / (tp + fp) # Correct? was written as (fp / (tp / fp)) in paper
        splitting      = fn / (tn + fn)
        error          = (fp + fn) / s
        del clusters, reference_clusters
        return dict(locals())

def unpack(clusters, reference_clusters):
    # Calculate pairwise true/false positives/negatives
    article_count = sum(len(c) for c in clusters)
    all_ids       = list(set().union(e for c in reference_clusters for e in c))
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    s = 0
    for i, j in itertools.combinations(all_ids, r=2):
        s += 1
    for i, j in itertools.combinations(all_ids, r=2):
        label = False
        for ref_cluster in reference_clusters:
            if i in ref_cluster and j in ref_cluster:
                label = True
                break
        for cluster in clusters:
            prediction = i in cluster and j in cluster
            if prediction:
                if label:
                    tp += 1
                else:
                    fp += 1
                break
        else:
            if label:
                fn += 1
            else:
                tn += 1
    assert tp + tn + fp + fn == s, f'Sanity check on confusion matrix FAILED: {tp} + {tn} + {fp} + {fn} != {s}'
    return tp, tn, fp, fn

def cluster_metrics(clusters, reference_clusters):
    with np.errstate(divide='ignore', invalid='ignore'):
        article_count    = np.int32(sum(len(c) for c in clusters))
        reference_count  = np.int32(sum(len(c) for c in reference_clusters))
        total_clusters   = np.int32(len(clusters))
        true_clusters    = np.int32(len(reference_clusters))
        total_authors    = np.int32(true_clusters)

        all_ids          = list(set().union(e for c in reference_clusters for e in c))
        if len(all_ids) == 0 or true_clusters == 0 or total_clusters == 0:
            raise IncompleteValidation(f'Incomplete, true: {true_clusters}, total: {total_clusters}')
        else:
            pass
            # print(f'Complete,   true: {true_clusters}, total: {total_clusters}')
        correct_clusters = np.int32(0)
        for cluster in clusters:
            if cluster in reference_clusters:
                correct_clusters += 1

        cluster_precision  = cp = np.float32(correct_clusters / total_clusters)
        cluster_recall     = cr = np.float32(correct_clusters / true_clusters)
        cluster_f1              = np.float32((2 * cp * cr) / (cp + cr))

        cluster_ratio           = np.float32(total_clusters / true_clusters)

        cluster_purity = 0
        for i in range(total_clusters):
            for j in range(true_clusters):
                correct   = len({k for k in clusters[i] if k in reference_clusters[j]})
                normalize = len(clusters[i])
                if normalize > 0:
                    cluster_purity += correct ** 2 / normalize
                else:
                    cluster_purity = 0.
        cluster_purity = cluster_purity / total_authors

        author_purity = 0
        # for i in range(true_clusters):
        #     for j in range(total_clusters):
        #         correct   = len({k for k in clusters[i] if k in reference_clusters[j]})
        #         normalize = len(clusters[i])
        #         author_purity += correct ** 2 / normalize
        # author_purity = author_purity / total_authors
        del i, j, correct, normalize

        k_measure = np.sqrt(cluster_purity * author_purity)

        contained = lambda s, cs : [c for c in cs if s in c][0]

        b_cubed_precision = 0
        b_cubed_recall    = 0
        # for s in range(1, total_authors + 1):
        try:
            for s in all_ids:
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
            # Don't return these
            del s, all_ids, cluster
            del clusters, reference_clusters, V, T, C, U, ref_recall, ref_precision, contained

            b_cubed_precision = bp =  b_cubed_precision / total_authors
            b_cubed_recall    = br =  b_cubed_recall / total_authors
            b_cubed_f1             = (2 * bp * br) / (bp + br)
        except IndexError:
            raise IncompleteValidation('Incomplete')
        return dict(locals())

def to_clusters(labels):
    ''' Convert labels of the form {article_id : cluster_id} to clusters of the form
        [{article_id..}..]'''
    # print('labels', labels)
    clusters = []
    for k, v in sorted(labels.items(), key=lambda t : t[1]):
        if len(clusters) < v + 1:
            clusters.append(set())
        clusters[v].add(k)
    return clusters
