from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import SelfCitationResolver, batched

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    blocks         = client.reference_sets['first_initial_last_name']

    client.validation.drop_collection('self_citations')
    self_cites_collection = client.validation.self_citations

    query = {}
    resolver = SelfCitationResolver(client, 'self_citations')

    skip = self_cites_collection.count_documents({})
    for batch in batched(resolver.create(client, blocks, articles, query=query, skip=skip),
                         batch_size=32):
        self_cites_collection.insert_many(batch)
