
from rich.pretty import pprint
from resolution.database.client import get_client

def run():
    print('Checking articles in MongoDB', flush=True)
    get_client('mongo_credentials.json', local=False)

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
