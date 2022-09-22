from pymongo import MongoClient
from rich.pretty   import pprint

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl
    n = bhl.count_documents({})

    print(f'Found {n} BHL clusters')
    for doc in bhl.find():
        pprint(doc)
        break
        jstor_article = articles.find_one({'authors.key' : doc['author']['key']})
    # pprint(articles.find_one({'authors.key' : 'aborstlap'}))
