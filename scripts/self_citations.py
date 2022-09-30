from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    # blocks         = client.reference_sets['block'] # Smaller, maybe too restrictive
    blocks         = client.reference_sets['last'] # Much bigger

    client.validation.drop_collection('self_citations')
    self_cites_collection = client.validation.self_citations
    self_cites_collection.insert_many(self_citations(blocks, articles))