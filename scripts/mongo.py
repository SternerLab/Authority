from pymongo import MongoClient
from rich.pretty import pprint

def run():
    print('Testing mongo DB', flush=True)
    client = MongoClient('localhost', 27017)

    database = client.test

    collect = database.test

    collect.insert_one({'hello' : 'world'})

    print(collect.find_one())

