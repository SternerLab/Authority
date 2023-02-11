
from rich.pretty   import pprint

from resolution.validation.self_citations import SelfCitationResolver, batched
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)

    # client.validation.drop_collection('self_citations')
    self_cites_collection = client.validation.self_citations

    query = {}
    resolver = SelfCitationResolver(client, 'self_citations')

    skip = self_cites_collection.count_documents({})
    for batch in batched(resolver.create(client, query=query, skip=skip), batch_size=32):
        self_cites_collection.insert_many(batch)
