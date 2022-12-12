from pymongo import MongoClient
from rich.pretty import pprint


def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    collect = jstor_database.articles

    lookup    = client.reference_sets_group_lookup['first_initial_last_name']
    inference = client.inferred['first_initial_last_name']
    print(f'lookup: {lookup.count_documents({})}')
    print(f'inference: {inference.count_documents({})}')
