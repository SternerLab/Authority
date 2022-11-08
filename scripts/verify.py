from pymongo import MongoClient
from rich.pretty import pprint

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    collect = jstor_database.articles

    pprint(collect.find_one({'authors.last' : 'heimerl'}))
    # 1/0

    n = collect.count_documents({})
    print(f'{n} articles!')
    return

    count = 0
    for article in collect.find():
        count += 1
        pprint(article['authors'])
        pprint(article['title'])
        pprint(article['journal'])
        pprint(article)
        break
    print(f'Counted {count} articles!', flush=True)
