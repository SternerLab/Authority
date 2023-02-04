
from rich.pretty import pprint

from resolution.database.client import get_client

def run():
    print('Checking articles in MongoDB', flush=True)
    get_client('mongo_credentials.json', local=False)

    jstor_database = client.jstor_database
    collect = jstor_database.articles

    lookup    = client.reference_sets_group_lookup['first_initial_last_name']
    inference = client.inferred['first_initial_last_name']
    print(f'lookup: {lookup.count_documents({})}')
    print(f'inference: {inference.count_documents({})}')
