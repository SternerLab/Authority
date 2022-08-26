from pymongo import MongoClient
from rich.pretty import pprint
import itertools
import pymongo

from authority.validation.google_scholar import get_clusters

def run():
    client = MongoClient('localhost', 27017)
    jstor_database   = client.jstor_database
    scholar_db       = client.google_scholar
    scholar_authors  = scholar_db.authors
    articles         = jstor_database.articles

    count = 0
    for cluster in scholar_authors.find():
        pprint(cluster)
        count += 1
    print(f'There are {count} reference clusters in the google scholar authors collection')