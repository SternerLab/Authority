from pymongo import MongoClient
from rich.pretty import pprint
import rich.prompt

def run():
    print('Listing all databases and collections in current MongoDB', flush=True)
    client = MongoClient('localhost', 27017)
    for database_name in client.list_database_names():
        print(f'{database_name}:')
        for collection_name in client[database_name].list_collection_names():
            print(f'    {collection_name}')


