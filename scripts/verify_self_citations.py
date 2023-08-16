from bson.objectid import ObjectId

from rich.pretty   import pprint
from rich.progress import track
from rich import print

from resolution.validation.self_citations import SelfCitationResolver, batched
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    # blocks         = client.reference_sets['block']
    blocks         = client.reference_sets['last_name']

    self_cites_collection = client.validation.self_citations

    n = self_cites_collection.count_documents({})
    print(f'There are {n} self citation documents')

    query = {}

    for doc in track(self_cites_collection.find(query), description='Checking citations', total=n):
        l = sum(len(v) for k, v in doc.items() if isinstance(v, list))
        pprint(doc)
        break
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
