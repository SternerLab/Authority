
from rich.pretty import pprint

def run():
    print('Checking articles in MongoDB', flush=True)
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    collect = jstor_database.articles

    # pprint(collect.find_one({'authors.key' : 'zli'}))
    # 1/0
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
