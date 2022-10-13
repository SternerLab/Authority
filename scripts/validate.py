from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle

from bson.objectid import ObjectId

from authority.validation.metrics import *
from authority.validation.self_citations import resolve

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['first_initial_last_name']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    val            = client.validation
    bhl            = val.bhl
    scholar        = val.google_scholar_doi
    self_citations = val.self_citations
    self_citations.create_index('authors_id')
    self_citations.create_index('authors.key')

    query = {}
    name = 'aaagaard'
    first_initial, *last = name
    last = ''.join(last)
    query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}
    # query = {}

    print('Validating..')
    print(inferred_blocks.find({}))

    try:

        for cluster in inferred_blocks.find(query):
            gid = cluster['group_id']
            if gid["first_initial"] == '':
                continue
            name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
            self_citation_labels = resolve(cluster, self_citations)
            print(name)
            pprint(self_citation_labels)
            cluster_labels = cluster['cluster_labels']
            pprint(cluster_labels)
            reference_clusters = to_clusters(self_citation_labels)
            shared_predictions = {k : v for k, v in cluster['cluster_labels'].items()
                                  if k in self_citation_labels}
            predicted_clusters = to_clusters(shared_predictions)
            pprint(reference_clusters)
            pprint(predicted_clusters)
            clusterwise = cluster_metrics(predicted_clusters, reference_clusters)
            pairwise    = pairwise_metrics(predicted_clusters, reference_clusters)
            pprint(clusterwise)
            pprint(pairwise)
    except KeyboardInterrupt:
        pass
