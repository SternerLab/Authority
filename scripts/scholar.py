from pymongo import MongoClient
from rich.pretty import pprint
import itertools
import pymongo

from authority.validation.google_scholar import get_clusters

def run():
    client = MongoClient('localhost', 27017)
    jstor_database   = client.jstor_database
    scholar          = client.validation.google_scholar
    articles         = jstor_database.articles

    with articles.find(no_cursor_timeout=True) as article_cursor:
        for article in article_cursor:
            pprint(article['title'])
            pprint(article['authors'])
            for cluster in get_clusters(article):
                pprint(cluster)
                scholar.update_one(
                        {'scholar_id' : cluster['scholar_id']},
                        {'$set' : cluster}, True)
