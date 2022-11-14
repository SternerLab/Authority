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

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    val            = client.validation
    bhl            = val.bhl
    scholar        = val.google_scholar_doi
    self_citations = val.self_citations
    self_citations.create_index('authors_id')
    self_citations.create_index([('authors.key', pymongo.ASCENDING)])

    name = 'bjohnson'
    first_initial, *last = name
    last = ''.join(last)
    query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}
    query = {}

    clusters = client.previous_inferred.previous_inferred

    print('Building self-citation cache')
    self_citation_cache = build_self_citation_cache(self_citations)
    print('Done!')

    try:
        long = []
        for i, cluster in enumerate(clusters.find(query)):
            try:
                gid = cluster['group_id']
                if gid["first_initial"] == '':
                    continue
                name = f'{gid["first_initial"].title()}. {gid["last"].title()}'

                self_citation_labels = resolve(cluster, self_citation_cache)

                upper_bound = len(self_citation_labels) ** 2

                print(name)
                print('self_cite_labels', self_citation_labels)
                reference_clusters = to_clusters(self_citation_labels)
                shared_predictions = {k : v for k, v in cluster['cluster_labels'].items()
                                      if k in self_citation_labels}
                shared_predictions = make_contiguous(shared_predictions)
                print('shared_predictions', shared_predictions)
                print(len(shared_predictions))
                predicted_clusters = to_clusters(shared_predictions)
                clusterwise = cluster_metrics(predicted_clusters, reference_clusters)
                pairwise    = pairwise_metrics(predicted_clusters, reference_clusters)

                pprint(clusterwise)
                pprint(pairwise)

                clusterwise.update(pairwise)
                clusterwise['name'] = name
            except KeyboardInterrupt:
                raise
            except IncompleteValidation:
                continue # pass
            if clusterwise['s'] > 0:
                long.append(clusterwise)
            if i % 16 == 0:
                running = pd.DataFrame(long)
                print(running.describe()[['accuracy', 'precision', 'recall', 'lumping', 'splitting']])
                print(running[['tp', 'tn', 'fp', 'fn', 's']])
    except KeyboardInterrupt:
        pass
    finally:
        running = pd.DataFrame(long)
        print(running.describe()[['accuracy', 'precision', 'recall', 'lumping', 'splitting']])
        print(running[['tp', 'tn', 'fp', 'fn', 's']])
        running.to_csv('data/authority_validation_metrics.csv')
