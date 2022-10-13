from bson.objectid import ObjectId
from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich import print

from authority.validation.self_citations import self_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    # blocks         = client.reference_sets['block']
    blocks         = client.reference_sets['last_name']

    self_cites_collection = client.validation.self_citations

    n = self_cites_collection.count_documents({})
    print(f'There are {n} self citation documents')

    key = 'aaagaard'
    query = {'author.key' : key}

    running = 0
    for doc in track(self_cites_collection.find(query), description='Checking citations', total=n):
        l = sum(len(v) for k, v in doc.items() if isinstance(v, list))
        pprint(doc)
        for k, v in doc.items():
            if k != '_id':
                matching = articles.find_one({'title' : k})
                if matching is not None:
                    print(matching['authors'])
                else:
                    print('No matching article?')
        running += l
        print(running, 'total citations in all clusters')

    print(f'There are {n} self citation documents')
