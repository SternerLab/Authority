from pymongo import MongoClient
from rich.pretty import pprint
from authority.lib import hello

def run():
    print('Checking articles in MongoDB', flush=True)
    hello()
    client = MongoClient('localhost', 27017)

    database = client.articles

    collect = database.main

    pprint(collect.find_one())
