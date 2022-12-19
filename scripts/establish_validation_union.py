from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import dill as pickle

from bson.objectid import ObjectId

import seaborn as sns
import matplotlib.pyplot as plt

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['block']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    val            = client.validation
    bhl            = val.bhl
    scholar        = val.google_scholar_doi
    self_citations = val.self_citations

    pprint(bhl.find_one())
    pprint(scholar.find_one())
    pprint(self_citations.find_one())

    total_found_clusters = 0
    for cluster in inferred_blocks.find():
        found_clusters = 0
        for mongo_id, cluster_label in cluster['cluster_labels'].items():
            cite_cluster = self_citations.find_one({'_id' : ObjectId(mongo_id)})
            if cite_cluster is not None:
                found_clusters += 1
            else:
                # print(f'id={mongo_id} not found in self-citations')
                pass
            total_found_clusters += found_clusters
        print(cluster['group_id'], f'found {found_clusters} clusters ({total_found_clusters} total)')

    total_article_clusters = 0
    for article in articles.find():
        cite_cluster = self_citations.find_one({'_id' : ObjectId(article['_id'])})
        if cite_cluster is not None:
            total_article_clusters += 1
    print(f'There are {total_article_clusters} valid clusters')
