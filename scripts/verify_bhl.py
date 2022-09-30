from pymongo import MongoClient
from rich.pretty   import pprint

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    bhl = client.validation.bhl
    n = bhl.count_documents({})

    print(f'Found {n} BHL clusters')
    for doc in bhl.find():
        # pprint(doc['author']['key'])
        if 'jstor_article_mongo_ids' in doc:
            pprint(doc)

        # for title in doc['titles']:
        #     pprint(title)
        #     jstor_article = articles.find_one({'title' : title})
        #     if jstor_article is not None:
        #         pprint(jstor_article['title'])
        #         pprint(jstor_article['authors'])
        # jstor_article = articles.find_one({'authors.key' : doc['author']['key']})
        # if jstor_article is not None:
        #     pprint(jstor_article['title'])
        #     pprint(jstor_article['authors'])
