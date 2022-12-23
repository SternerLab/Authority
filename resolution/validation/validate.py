from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich import print
import itertools
import dill as pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

import logging
log = logging.getLogger('rich')

from .utils   import *
from .metrics import *
from .manual          import ManualResolver
from .self_citations  import SelfCitationResolver
from .google_scholar  import GoogleScholarResolver
from .biodiversity    import BiodiversityResolver
from .orcid           import OrcidResolver
from .heuristic       import HeuristicResolver, possible_heuristics

possible_sources = (['self_citations', 'google_scholar', 'biodiversity', 'orcid', 'manual']
                    + list(possible_heuristics.keys()))
excluded_references = {'split_heuristic', 'merge_heuristic'}

def load_sources(client, source_names):
    ''' Resolve multiple sources to their reference clusters '''
    sources = dict()
    for source_name in source_names:
        match source_name:
            case 'self_citations':
                sources[source_name] = SelfCitationResolver(client, source_name)
            case 'google_scholar':
                sources[source_name] = GoogleScholarResolver(client, source_name)
            case 'biodiversity':
                sources[source_name] = BiodiversityResolver(client, source_name)
            case 'orcid':
                sources[source_name] = OrcidResolver(client, source_name)
            case 'manual':
                sources[source_name] = ManualResolver(client, source_name)
            case _:
                if 'heuristic' in source_name:
                    kind, _ = source_name.split('_')
                    assert kind in possible_heuristics, f'{kind} not in possible heuristics {possible_heuristics.keys()}'
                    sources[source_name] = HeuristicResolver(client, kind)
                else:
                    print(f'{source_name} not recognized!')
        if source_name not in sources:
            print(f'Source {source_name} not in possible sources: {possible_sources}')
    for source in sources.values():
        source.build_cache()
    return sources


def create_labeled_clusters(client, cluster, sources, prediction_source):
    predicted_labels   = cluster['cluster_labels']
    predicted_clusters = to_clusters(predicted_labels)
    all_clusters = {prediction_source : (predicted_clusters, predicted_labels)}
    for source_name, source in sources.items():
        labels = source.resolve(cluster)
        if 'meshcoauthor' in source_name or 'name' in source_name:
            log.info(f'{source_name} resolved {labels}')
        if isinstance(labels, dict):
            reference_clusters = to_clusters(labels)
        else:
            reference_clusters = labels
        all_clusters[source_name] = (reference_clusters, labels)
    return all_clusters

def to_shared_clusters(clusters_or_labels, shared):
    if not isinstance(clusters_or_labels, list):
        # print(f'Converting labels to shared clusters')
        shared_labels = {k : v for k, v in clusters_or_labels.items()
                              if k in shared}
        shared_labels = make_contiguous(shared_labels)
        shared_clusters = to_clusters(shared_labels)
        # print('result', shared_clusters)
    else:
        # print(f'Converting clusters to shared clusters')
        shared_clusters = [set(s for s in c if s in shared)
                              for c in clusters_or_labels]
        shared_clusters = [c for c in shared_clusters if len(c) > 0]
        # print('result', shared_clusters)
    return shared_clusters

def get_shared_ids(pred_clusters, ref_clusters):
    pred_unique = set(s for cluster in pred_clusters for s in cluster)
    ref_unique  = set(s for cluster in ref_clusters for s in cluster)
    return pred_unique & ref_unique

def compare_cluster_pair(pair):
    ((predicted_source, (predicted_clusters, predicted_labels)),
     (reference_source, (reference_clusters, predicted_labels))) = pair
    shared = get_shared_ids(predicted_clusters, reference_clusters)
    # print(f'sources: {predicted_source}, {reference_source}')
    # print('original predicted', predicted_clusters)
    shared = get_shared_ids(predicted_clusters, reference_clusters)
    predicted_clusters = to_shared_clusters(predicted_clusters, shared)
    # print('original reference', reference_clusters)
    reference_clusters = to_shared_clusters(reference_clusters, shared)

    metrics  = cluster_metrics(predicted_clusters, reference_clusters)
    pairwise = pairwise_metrics(predicted_clusters, reference_clusters)
    metrics.update(pairwise)
    metrics['prediction_source'] = predicted_source
    metrics['reference_source']  = reference_source

    sk_metrics = sklearn_metrics(predicted_clusters, reference_clusters)
    metrics.update(sk_metrics)

    # print(predicted_source, reference_source)
    # print(metrics)
    return metrics

def _validation_generator(pairs, name):
    complete = 0
    for pair in pairs:
        ((predicted_source, _),
         (reference_source, _)) = pair
        if predicted_source == reference_source or reference_source in excluded_references:
            continue
        try:
            metrics = compare_cluster_pair(pair)
            metrics['name'] = name
            if metrics['s'] > 0:
                yield metrics
                complete += 1
        except IncompleteValidation as e:
            pass
    if complete == 0:
        log.warning(f'Source had incomplete resolution incomplete: {name}')
        yield from []

def validate(client, cluster, sources, prediction_source, is_first):
    ''' Validate a single cluster against multiple reference sources '''
    all_clusters = create_labeled_clusters(client, cluster, sources, prediction_source)
    gid = cluster['group_id']
    name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
    pairs = itertools.product(all_clusters.items(), repeat=2)
    if not is_first:
        pairs = ((a, b) for (a, b) in pairs if prediction_source in {a[0], b[0]})
    bound = len(all_clusters) ** 2
    return bound, _validation_generator(pairs, name)

def validate_all(client, prediction_sources, query, sources):
    total = 0
    generator = None
    for i, (name, inferred) in enumerate(prediction_sources.items()):
        is_first = i == 0
        print(f'Validating {name}!')
        inferred_size = inferred.count_documents({})
        for i, cluster in track(enumerate(inferred.find(query)), total=inferred_size,
                                description='Creating validation generator'):
            if isinstance(cluster['cluster_labels'], list):
                cluster['cluster_labels'] = cluster['cluster_labels'][0]
            try:
                if cluster['group_id']['first_initial'] == '':
                    continue
                bound, next_generator = validate(client, cluster, sources, name,
                                                 is_first=is_first)
                expected = bound * inferred_size
                total += bound
                if generator is None:
                    generator = next_generator
                else:
                    generator = itertools.chain(generator, next_generator)
            except KeyboardInterrupt:
                print(f'Exited validation!')
                break
            if i % 1000 == 0:
                print(f'{total}/{expected} : {(total / expected ):2.2%}')
    print(f'Finished creating validation generators')
    generator = track(generator, total=total, description='Validation')
    return generator
