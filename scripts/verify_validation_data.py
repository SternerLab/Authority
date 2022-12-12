from pymongo import MongoClient
from rich.pretty import pprint


def run():
    print('Checking articles in MongoDB', flush=True)
    client     = MongoClient('localhost', 27017)
    validation = client.validation

    for val_type in validation.list_collection_names():
        coll = validation[val_type]
        print(f'{val_type}: {coll.count_documents({})}')
