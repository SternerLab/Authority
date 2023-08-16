
from rich.pretty   import pprint
from rich.progress import track
from rich.progress import Progress
from functools import partial
import itertools
import pymongo
import pandas as pd

from resolution.validation.google_scholar import get_clusters
from resolution.database.client import get_client
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
    client = get_client('mongo_credentials.json', local=True)
    jstor_database   = client.jstor_database
    scholar          = client.validation.google_scholar_dois
    articles         = jstor_database.articles

    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)

    with client.start_session(causal_consistency=True) as session:
        for key in names['key']:
            query = {'authors.key' : key}
            article = articles.find_one(query, no_cursor_timeout=True, session=session)
            parse_scholar_article(article, scholar=scholar)
