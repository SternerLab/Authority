from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from .utils   import *
from .metrics import *
from .self_citations import SelfCitationResolver
from .google_scholar import GoogleScholarResolver
from .biodiversity   import BiodiversityResolver

possible_sources = ['self_citations', 'google_scholar', 'biodiversity', 'manual']

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
                print(f'Source {source_name} is not in possible sources: {__possible_sources__}')
    for source in sources.values():
        source.build_cache()
    return sources

def validate(cluster, sources):
    ''' Validate a single cluster against multiple reference sources '''
    long = []
    for source_name, source in sources.items():
        try:
            gid = cluster['group_id']
            if gid["first_initial"] == '':
                continue
            name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
            print(name)
            labels             = source.resolve(cluster)
            reference_clusters = to_clusters(labels)
            shared_predictions = {k : v for k, v in cluster['cluster_labels'].items()
                                  if k in labels}
            shared_predictions = make_contiguous(shared_predictions)
            predicted_clusters = to_clusters(shared_predictions)

            clusterwise = cluster_metrics(predicted_clusters, reference_clusters)
            pairwise    = pairwise_metrics(predicted_clusters, reference_clusters)
            clusterwise.update(pairwise)
            clusterwise['name'] = name
            clusterwise['source_name'] = name

            pprint(clusterwise)
            if clusterwise['s'] > 0:
                long.append(clusterwise)
        except IncompleteValidation: # Handle this better TODO ?
            # Not dangerous, should just log something..
            continue

    running = pd.DataFrame(long)
    return running

def validate_clusters(inferred, query, sources):
    for i, cluster in enumerate(inferred.find()):
        metrics = validate(cluster, sources)
