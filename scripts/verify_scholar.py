from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
import itertools
import pymongo
from bson.objectid import ObjectId

from authority.validation.google_scholar import get_clusters

def run():
    client = MongoClient('localhost', 27017)
    jstor_database   = client.jstor_database
    scholar           = client.validation.google_scholar_dois
    articles         = jstor_database.articles

    # │   'author': {
    # │   │   'key': 'akurisaki',

    for doc in scholar.find({'author.key' : 'acolpaert'}):
        print(doc)

    for doc in scholar.find({'mongo_ids' : ObjectId('6337e27cf3513987bb925152')}):
        print(doc)

    # for doc in scholar.find():
    #     print(doc)
