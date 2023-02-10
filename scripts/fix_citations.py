
from rich.pretty   import pprint
from rich.progress import track
from rich import print

from resolution.parse.parse import parse_citations

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    n = articles.count_documents({})
    print(f'Found {n} articles')

    for article in track(articles.find(), description='Updating citations', total=n):
        pprint(article['citations'])
        pprint(parse_citations(article))
        1/0
        articles.update_one({'_id' : article['_id']},
                {'$set' : {'citations' : parse_citations(article)}})
