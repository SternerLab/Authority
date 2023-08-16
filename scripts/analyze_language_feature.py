from rich.pretty import pprint
from bson.son import SON

from resolution.database.client import get_client

def run():
    print('Checking articles in MongoDB', flush=True)
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    articles = jstor_database.articles

    # for article in articles.find():
    #     print(article['language'])
    # for doc in articles.aggregate([{'$unwind' : '$language'}]):
    #     print(doc['language'])
    #     break

    pipeline = [{'$unwind' : '$language'},
                {'$group' : {'_id' : '$language', 'count' : {'$sum' : 1}}},
                {'$sort': SON([('count', -1), ('_id', -1)])}
                ]
    for doc in articles.aggregate(pipeline):
        print(doc)
