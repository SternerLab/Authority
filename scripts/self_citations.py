from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    blocks         = client.reference_sets['block']
    self_cites_collection = client.validation.self_citations

    for self_cites in self_citations(blocks, articles):
        self_cites_collection.insert_one(self_cites)
