
from rich.pretty   import pprint
from rich.progress import track

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    client.validation.drop_collection('biodiversity')
    client.validation.drop_collection('biodiversity_lookup')
