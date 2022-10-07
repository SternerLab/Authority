from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    blocks         = client.reference_sets['first_initial_last_name']
    # blocks         = client.reference_sets['last'] # Much bigger


    client.validation.drop_collection('self_citations')

    query = {}
    # query = {'group.authors.last' : 'heimerl'}
    # query = {'group.authors.last' : 'bjohnson'}
    # query = {'group.authors.last' : 'bschirone'}

    self_cites_collection = client.validation.self_citations
    self_cites_collection.insert_many(self_citations(blocks, articles, query=query))
