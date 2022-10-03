import sqlite3
from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
import itertools
import pymongo
from authority.validation.google_scholar import parse_google_scholar_name
from authority.parse.parse import remove_stop_words

''' Parse 24,763 google scholar articles from previous sqlite3 db '''

table    = 'google_scholar_new'
all_rows = 'SELECT * from {}'

def expand_author_row(row, articles):
    _, ids, full_name, scholar_id = row
    name = parse_google_scholar_name(full_name)
    pprint(name)
    mongo_ids = []
    titles    = []
    dois      = []
    for doi in ids.split(','):
        article = articles.find_one({'front.article-meta.article-id.#text' : doi})
        if article is not None:
            mongo_ids.append(article['_id'])
            titles.append(article['title'])
        else: # :(
            mongo_ids.append(None)
            titles.append(None)
        dois.append(doi)
    pprint(dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids))
    return dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids)

def run():
    mongo_client = MongoClient('localhost', 27017)

    sql_client   = sqlite3.connect('database/jstor-authority.db')
    sql_cursor   = sql_client.cursor()

    jstor_database    = mongo_client.jstor_database
    mongo_client.validation.drop_collection('google_scholar_dois')
    scholar           = mongo_client.validation.google_scholar_dois
    articles          = jstor_database.articles

    sql_cursor.execute(all_rows.format(table))
    for row in sql_cursor.fetchall():
        scholar.insert_one(expand_author_row(row, articles))

