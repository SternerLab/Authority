from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle

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


    for cluster in inferred_blocks.find():
        pprint(cluster['group_id'])
        pprint(cluster['cluster_labels'])
        probs = pickle.loads(cluster['probs'])
        print(probs)
