from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from authority.validation.metrics import *
from authority.validation.self_citations import resolve, make_contiguous, build_self_citation_cache

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    # inferred       = client.inferred
    # inferred_blocks = inferred['first_initial_last_name']
    # inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    inferred_blocks = client.previous_inferred.previous_inferred

    val            = client.validation
    scholar        = val.google_scholar_dois # !!

    name = 'zli'
    # name = 'bjohnson'
    first_initial, *last = name
    last = ''.join(last)
    query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}
    query = {}

    try:
        long = []
        i = 0
        for i, cluster in enumerate(inferred_blocks.find(query)):
            try:
                gid = cluster['group_id']
                key = f'{gid["first_initial"]}{gid["last"]}'
                name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
                print(gid)
                print(key)
                print(name)

                # can resolve by author.key, title, or mongo_ids
                # use key:
                reference_clusters = []
                resolved = 0
                for doc in scholar.find({'author.key' : key}):
                    reference_clusters.append([str(_id) for _id in doc['mongo_ids']])
                    resolved += 1
                if resolved > 0:
                    print('resolved', resolved)

                unique = set(s for cluster in reference_clusters for s in cluster)
                print(unique)

                print(name)
                print(reference_clusters)
                print(cluster['cluster_labels'])
                shared_predictions = {k : v for k, v in cluster['cluster_labels'].items()
                                      if k in unique}
                shared_predictions = make_contiguous(shared_predictions)
                print('shared_predictions', shared_predictions)
                print(len(shared_predictions))
                predicted_clusters = to_clusters(shared_predictions)
                if predicted_clusters and reference_clusters:
                    clusterwise = cluster_metrics(predicted_clusters, reference_clusters)
                    pairwise    = pairwise_metrics(predicted_clusters, reference_clusters)

                    pprint(clusterwise)
                    pprint(pairwise)

                    clusterwise.update(pairwise)
                    clusterwise['name'] = name
                    if clusterwise['s'] > 0:
                        long.append(clusterwise)
                    if i % 16 == 0:
                        running = pd.DataFrame(long)
                        print(running.describe()[['accuracy', 'precision', 'recall', 'lumping', 'splitting']])
                        print(running[['tp', 'tn', 'fp', 'fn', 's']])
            except IncompleteValidation:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        running = pd.DataFrame(long)
        print(running.describe()[['accuracy', 'precision', 'recall', 'lumping', 'splitting']])
        print(running[['tp', 'tn', 'fp', 'fn', 's']])
        running.to_csv('data/authority_scholar_validation_metrics.csv')

