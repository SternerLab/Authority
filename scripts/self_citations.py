from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    blocks         = client.reference_sets['first_initial_last_name']

    client.validation.drop_collection('self_citations')

    query = {}
    # query = {'group.authors.last' : 'bjohnson'}

    self_cites_collection = client.validation.self_citations
    # TO test changes without modifying db
    # for doc in self_citations(client, blocks, articles, query=query):
    #     pprint(doc)
    self_cites_collection.insert_many(self_citations(client, blocks, articles, query=query))
