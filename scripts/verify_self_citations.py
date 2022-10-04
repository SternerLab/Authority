from pymongo import MongoClient
from rich.pretty   import pprint

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    # blocks         = client.reference_sets['block']
    blocks         = client.reference_sets['last']

    self_cites_collection = client.validation.self_citations

    n = self_cites_collection.count_documents({})
    print(f'There are {n} self citation documents')

    for doc in self_cites_collection.find():
        pprint(doc)
    print(f'There are {n} self citation documents')
