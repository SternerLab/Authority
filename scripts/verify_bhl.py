from pymongo import MongoClient
from rich.pretty   import pprint

def run():
    client = MongoClient('localhost', 27017)

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl
    n = bhl.count_documents({})

    print(f'Found {n} BHL clusters')
