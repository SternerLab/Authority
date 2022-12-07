from pymongo import MongoClient
from rich.progress import track
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
    for doc in track(bhl.find(), total=n):
        ids = set()
        key = doc['author']['key']

        # Resolve by matching title, then author
        for title in doc['titles']:
            pprint(title)
            jstor_article = articles.find_one({'title' : title})
            if (jstor_article is not None and
                key in {a['key'] for a in jstor_article['authors']}):
                ids.add(jstor_article['_id'])
        # Resolve by author key
        for jstor_article in articles.find({'authors.key' : key}):
            if jstor_article is not None and jstor_article['title'] in doc['titles']:
                ids.add(jstor_article['_id'])

        if ids:
            pprint({'_id' : doc['_id'], '$push' : {'mongo_ids' : list(ids)}})

            bhl.update_one({'_id' : doc['_id']},
                           {'$push' : {'mongo_ids' : list(ids)}},
                           True)
