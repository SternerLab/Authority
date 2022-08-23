from pymongo import MongoClient
from rich.pretty import pprint

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    database = client.articles

    collect = database.main

    count = 0
    for article in collect.find():
        count += 1
        pprint(article['article']['authors'])
        pprint(article['article']['title'])
    print(f'Inserted {count} articles!', flush=True)
