from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich.progress import Progress
import itertools
import pymongo
from functools import partial


from authority.validation.google_scholar import get_clusters
from threading import Lock

count = 0


def parse_scholar_article(article, scholar=None):
    pprint(article['title'])
    pprint(article['authors'])
    for cluster in get_clusters(article):
        pprint(cluster)
        scholar.update_one(
                {'scholar_id' : cluster['scholar_id']},
                {'$set' : {'author' : cluster['author']},
                 '$push' : {'titles' : cluster['titles']}}, True)

def run():
    client = MongoClient('localhost', 27017)
    jstor_database   = client.jstor_database
    scholar          = client.validation.google_scholar
    articles         = jstor_database.articles

    threads = 1
    upper_bound = articles.count_documents({})

    with client.start_session(causal_consistency=True) as session:
            f = partial(parse_scholar_article, scholar=scholar)
            article_cursor = articles.find(
                    {'authors.last' : 'bjohnson'},
                    no_cursor_timeout=True, session=session)
            pool.map(f, article_cursor)
