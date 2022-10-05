from pymongo import MongoClient
from rich.pretty import pprint

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    collect = jstor_database.articles
    n = collect.count_documents({})

    count = 0
    for article in collect.find():
        if 'mesh' in article and article['mesh'] != '':
            count += 1
            pprint(article['mesh'])
            # pprint(article['authors'])
            # pprint(article['title'])
            # pprint(article['mesh'])
            # pprint(article)

    print(f'Counted {count} mesh articles of {n} total documents!', flush=True)
