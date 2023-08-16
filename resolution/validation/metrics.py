import pandas as pd
from rich import print
from rich.pretty import pprint
from collections import namedtuple
import numpy as np
import itertools
import logging
import sklearn.metrics.cluster as skl_cluster_metrics

from .utils import *

class IncompleteValidation(Exception):
    pass

log = logging.getLogger('rich')

def pairwise_metrics(clusters, reference_clusters):
    tp, tn, fp, fn = (np.float32(v) for v in unpack(clusters, reference_clusters))
    # Don't ignore this!
    # with np.errstate(divide='ignore', invalid='ignore'):
    s         = tp + tn + fp + fn
    accuracy  = (tp + tn) / s
    precision = tp / (tp + fp)
    recall    = tp / (tp + fn)
    f1        = (2 * precision * recall) / (precision + recall)
    lumping   = fp / (tp + fp)
    splitting = fn / (tn + fn)
    error     = (fp + fn) / s
    pos_ratio = (tp + fp) / s
    neg_ratio = (tn + fn) / s
    if len(reference_clusters) > 1:
        tn_ratio       = tn / (tn + tp)
        neg_recall     = tn / (tn + fp)
        neg_precision  = tn / (tn + fn)
        neg_f1         = (2 * neg_precision * neg_recall) / (neg_precision + neg_recall)
        alt_lumping    = 1 - neg_precision
        balanced_accuracy = (recall + neg_recall) / 2
        adjusted_balanced_accuracy = (balanced_accuracy - 0.5) / (0.5)
    else:
        tn_ratio = np.nan
        neg_f1 = np.nan
        neg_precision = np.nan
        neg_recall = np.nan
        balanced_accuracy = np.nan
        adjusted_balanced_accuracy = np.nan
        alt_lumping = np.nan
    del clusters, reference_clusters
    return dict(locals())

def labels_to_array(labels):
    ''' Turn label dicts to arrays for sklearn '''
    array = [t[1] for t in sorted(labels.items(), key=lambda t : t[0])]
    return array

def clusters_to_labels(clusters):
    labels = dict()
    for i, cluster in enumerate(clusters):
        for key in cluster:
            labels[key] = i
    return labels

__sklearn_metrics = ['rand', 'adjusted_rand', 'adjusted_mutual_info',
                     'homogeneity', 'completeness', 'v_measure', 'fowlkes_mallows']
__sklearn_indices = ['calinski_harabasz', 'silhouette', 'davies_bouldin']

def sklearn_metrics(clusters, reference_clusters, features=None):

    preds = labels_to_array(clusters_to_labels(clusters))
    ref   = labels_to_array(clusters_to_labels(reference_clusters))

    try:
        metrics = {m : max(getattr(skl_cluster_metrics, f'{m}_score')(ref, preds), 0.)
                   for m in __sklearn_metrics}
    except ValueError:
        raise
    # If we had a per-article feature vector, we could use these, but we'll skip them.
    # if features is not None:
    #     for index in __sklearn_indices:
    #         index_kwargs = dict()
    #         if index == 'silhouette':
    #             index_kwargs['metric'] = 'euclidean'
    #         for source, labels in (('predictions', preds), ('reference', ref)):
    #             index_fn = getattr(sklearn_cluster_metrics, f'{index}_score')
    #             print(labels)
    #             try:
    #                 metrics[f'{index}_{source}'] = index_fn(features, labels, **index_kwargs)
    #             except ValueError as e:
    #                 print(e)
    #                 metrics[f'{index}_{source}'] = None
    # else:
    #     print(f'Features was none!')
    return metrics

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
                s += 1
                break
        else:
            if label:
                fn += 1
            else:
                tn += 1
            s += 1
    assert tp + tn + fp + fn == s, f'Sanity check on confusion matrix FAILED: {tp} + {tn} + {fp} + {fn} != {s}'
    return tp, tn, fp, fn

def cluster_metrics(clusters, reference_clusters):
    raise NotImplementedError('Cluster metrics deprecated in favor of sklearn metrics')
    with np.errstate(divide='ignore', invalid='ignore'):
        article_count    = np.int32(sum(len(c) for c in clusters))
        reference_count  = np.int32(sum(len(c) for c in reference_clusters))
        total_clusters   = np.int32(len(clusters))
        true_clusters    = np.int32(len(reference_clusters))
        total_authors    = np.int32(true_clusters)

        all_ids          = list(set().union(e for c in reference_clusters for e in c))
        if len(all_ids) == 0 or true_clusters == 0 or total_clusters == 0:
            raise IncompleteValidation(f'Incomplete, true: {true_clusters}, total: {total_clusters}')
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

        # Leave these be for now!
        # contained = lambda s, cs : [c for c in cs if s in c][0]

        # b_cubed_precision = 0
        # b_cubed_recall    = 0
        # # for s in range(1, total_authors + 1):
        # try:
        #     for s in all_ids:
        #         V = contained(s, clusters)
        #         T = {si for si in V
        #              if contained(si, reference_clusters) == contained(s, reference_clusters)}
        #         ref_precision = len(T)/len(V)
        #         b_cubed_precision += ref_precision

        #         C = contained(s, reference_clusters)
        #         U = {si for si in C
        #              if contained(si, clusters) == contained(s, clusters)}
        #         ref_recall    = len(U)/len(C)
        #         b_cubed_recall += ref_recall
        #     # Don't return these
        #     del s, all_ids, cluster
        #     del clusters, reference_clusters, V, T, C, U, ref_recall, ref_precision, contained

        #     b_cubed_precision = bp =  b_cubed_precision / total_authors
        #     b_cubed_recall    = br =  b_cubed_recall / total_authors
        #     b_cubed_f1             = (2 * bp * br) / (bp + br)
        # except IndexError:
        #     raise
        #     # raise IncompleteValidation('Incomplete')
        return dict(locals())

def to_clusters(labels):
    ''' Convert labels of the form {article_id : cluster_id} to clusters of the form
        [{article_id..}..]'''
    # print('to_clusters', labels)
    labels = contiguous(labels)
    clusters = []
    for k, v in sorted(labels.items(), key=lambda t : t[1]):
        if len(clusters) < v + 1:
            clusters.append(set())
        clusters[v].add(k)
    # print('result', clusters)
    return clusters
