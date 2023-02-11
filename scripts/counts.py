
from rich.pretty import pprint
import rich.prompt

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    print('Listing all databases and collections in current MongoDB', flush=True)
    for database_name in client.list_database_names():
        print(f'{database_name}:')
        for collection_name in client[database_name].list_collection_names():
            coll = client[database_name][collection_name]
            print(f'    {collection_name} {coll.count_documents({})}')


