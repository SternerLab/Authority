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

included_references = {'google_scholar', 'biodiversity', 'orcid'}
possible_sources = (['self_citations'] + list(included_references)
                    + list(possible_heuristics.keys()))

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
                    components = source_name.split('_')
                    kind = '_'.join(components[:-1])
                    assert kind in possible_heuristics, f'{kind} not in possible heuristics {possible_heuristics.keys()}'
                    sources[source_name] = HeuristicResolver(client, kind)
                else:
                    raise ValueError(f'{source_name} not recognized!')
        if source_name not in sources:
            raise ValueError(f'Source {source_name} not in possible sources: {possible_sources}')
    for source in sources.values():
        source.build_cache()
    return sources


def create_labeled_clusters(client, cluster, sources, prediction_source):
    predicted_labels   = cluster['cluster_labels']
    predicted_clusters = to_clusters(predicted_labels)
    all_clusters = {prediction_source : (predicted_clusters, predicted_labels)}
    for source_name, source in sources.items():
        labels = source.resolve(cluster)
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
     (reference_source, (reference_clusters, reference_labels))) = pair
    shared = get_shared_ids(predicted_clusters, reference_clusters)
    # print(f'sources: {predicted_source}, {reference_source}')
    # print('predicted', predicted_clusters)
    shared = get_shared_ids(predicted_clusters, reference_clusters)
    predicted_clusters = to_shared_clusters(predicted_clusters, shared)
    # print('reference', reference_clusters)
    reference_clusters = to_shared_clusters(reference_clusters, shared)

    # metrics  = cluster_metrics(predicted_clusters, reference_clusters)
    metrics = pairwise_metrics(predicted_clusters, reference_clusters)
    metrics['prediction_source'] = predicted_source
    metrics['reference_source']  = reference_source

    sk_metrics = sklearn_metrics(predicted_clusters, reference_clusters)
    metrics.update(sk_metrics)

    # print(predicted_source, reference_source)
    # print(metrics)
    return metrics

def _validation_generator(pairs, name):
    skipped  = 0
    complete = 0
    incomplete = 0
    for pair in pairs:
        ((predicted_source, (predicted_clusters, predicted_labels)),
         (reference_source, (reference_clusters, reference_labels))) = pair
        if (reference_source not in included_references and
            (predicted_source == reference_source)):
            continue
        try:
            n_labelled_clusters = len(reference_clusters)
            max_cluster_size    = max(len(c) for c in reference_clusters)
            # Post process skipping!
            if max_cluster_size > 0 and reference_source in included_references:
                metrics = compare_cluster_pair(pair)
                metrics['n_ref_clusters'] = len(reference_clusters)
                metrics['max_cluster_size'] = max_cluster_size
                metrics['name'] = name
                yield metrics
                complete += 1
            if n_labelled_clusters == 1:
                log.warn(f'Only one labelled cluster for {name}!')
            # if n_labelled_clusters > 1 and max_cluster_size > 1 and \
            #    reference_source in included_references:
            #     metrics = compare_cluster_pair(pair)
            #     metrics['n_ref_clusters'] = len(reference_clusters)
            #     metrics['max_cluster_size'] = max_cluster_size
            #     metrics['name'] = name
            #     yield metrics
            #     complete += 1
            # else:
            #     skipped += 1
        except IncompleteValidation as e:
            incomplete += 1
        except ValueError as e:
            skipped += 1
    if complete == 0:
        # log.warn(f'Source had incomplete resolution incomplete: {name}')
        yield from []
    if incomplete > 0:
        log.warn(f'After creating generator for {name}, there were {incomplete} incomplete comparisons')
        log.warn(f'    Also, there were {skipped} skipped comparisons due to lack of validation data')

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
    log.info('Beginning validation')
    total = 0
    generator = None
    for i, (name, inferred) in enumerate(prediction_sources.items()):
        is_first = i == 0
        log.info(f'Validating {name}!')
        inferred_size = inferred.count_documents({})
        for i, cluster in track(enumerate(inferred.find(query)), total=inferred_size,
                                description='Creating validation generator'):
            if isinstance(cluster['cluster_labels'], list):
                cluster['cluster_labels'] = cluster['cluster_labels'][0]
            try:
                if cluster['group_id']['first_initial'] == '': # Skip authors with no first initial
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
                log.warn(f'Exited validation! Please allow a clean exit')
                break
            if i % 1000 == 0:
                log.info(f'{total}/{expected} : {(total / expected ):2.2%}')
    log.info(f'Finished creating validation generators')
    generator = track(generator, total=total, description='Validation')
    return generator
