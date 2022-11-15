from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
import itertools
import pymongo

from authority.validation.google_scholar import get_clusters

def run():
    client = MongoClient('localhost', 27017)
    jstor_database   = client.jstor_database
    scholar          = client.validation.google_scholar_dois
    articles         = jstor_database.articles
    total = scholar.count_documents({})
    print(total)

    n_labels = 0
    for cluster in track(scholar.find(), total=total, description='Bounding labeled pairs'):
        # pprint(cluster)
        ids = cluster['mongo_ids']
        n_labels += len(ids) ** 2 - len(ids)
        print(n_labels)
    print(f'There are {n_labels} labels in the google scholar authors collection')
    print(f'There are {total} clusters in the google scholar authors collection')
