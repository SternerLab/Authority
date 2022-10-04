from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich import print

from authority.parse.parse import process_citations

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    n = articles.count_documents({})

    for article in track(articles.find(), description='Updating citations', total=n):
        articles.update_one({'_id' : article['_id']},
                {'$set' : {'citations' : process_citations(article)}})
