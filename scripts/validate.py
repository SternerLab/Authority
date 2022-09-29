from pymongo import MongoClient
from rich.pretty   import pprint

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['block']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl
    n = bhl.count_documents({})

    print(f'Found {n} BHL clusters')
    count = 0
    for doc in bhl.find():
        # flawed lookup method, update
        jstor_article = articles.find_one({'authors.key' : doc['author']['key']})
        if jstor_article is not None:
            print(jstor_article['title'])
            count += 1

    print(f'Found {count} corresponding JSTOR articles')
