from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from .utils   import *
from .metrics import *
from .manual          import ManualResolver
from .self_citations  import SelfCitationResolver
from .google_scholar  import GoogleScholarResolver
from .biodiversity    import BiodiversityResolver
from .heuristic       import HeuristicResolver, possible_heuristics

possible_sources = (['self_citations', 'google_scholar', 'biodiversity', 'manual']
                    + list(possible_heuristics.keys()))
excluded_references = {'split_heuristic', 'merge_heuristic', 'predicted'}

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

def create_labeled_clusters(cluster, sources):
    all_clusters = dict(predicted=(cluster['cluster_labels'], None))
    for source_name, source in sources.items():
        labels = source.resolve(cluster)
        if isinstance(labels, dict):
            reference_clusters = to_clusters(labels)
        else:
            reference_clusters = labels
        unique = set(s for cluster in reference_clusters for s in cluster)
        all_clusters[source_name] = (reference_clusters, unique)
    return all_clusters

def compare_cluster_pair(pair):
    ((predicted_source, (predicted_clusters, _)),
     (reference_source, (reference_clusters, unique))) = pair
    if not isinstance(predicted_clusters, list):
        shared_predictions = {k : v for k, v in predicted_clusters.items()
                              if unique is not None and k in unique}
        shared_predictions = make_contiguous(shared_predictions)
        predicted_clusters = to_clusters(shared_predictions)
    metrics  = cluster_metrics(predicted_clusters, reference_clusters)
    pairwise = pairwise_metrics(predicted_clusters, reference_clusters)
    metrics.update(pairwise)
    metrics['prediction_source'] = predicted_source
    metrics['reference_source']  = reference_source
    # print(predicted_source, reference_source)
    # print(metrics)
    return metrics

def validate(cluster, sources):
    ''' Validate a single cluster against multiple reference sources '''
    all_clusters = create_labeled_clusters(cluster, sources)
    long = []
    gid = cluster['group_id']
    name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
    for pair in itertools.product(all_clusters.items(), repeat=2):
        ((predicted_source, _),
         (reference_source, _)) = pair
        print(predicted_source, reference_source)
        if predicted_source == reference_source or reference_source in excluded_references:
            continue
        try:
            metrics = compare_cluster_pair(pair)
            metrics['name'] = name
            if metrics['s'] > 0:
                long.append(metrics)
        except IncompleteValidation as e:
            print(e)
    return long

def validate_clusters(inferred, query, sources):
    long = []
    for i, cluster in enumerate(track(inferred.find(query),
                                      total=inferred.count_documents(query),
                                      description='Validation')):
        try:
            if cluster['group_id']['first_initial'] == '':
                continue
            long.extend(validate(cluster, sources))
        except KeyboardInterrupt:
            print(f'Exited validation!')
            break
    running = pd.DataFrame(long)
    return running
