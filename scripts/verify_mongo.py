
from rich.pretty import pprint
from resolution.database.client import get_client

def run():
    print('Testing mongo DB', flush=True)
    client = get_client('mongo_credentials.json', local=True)

    database = client.test

    collect = database.test

    collect.insert_one({'hello' : 'world'})

    print(collect.find_one())

