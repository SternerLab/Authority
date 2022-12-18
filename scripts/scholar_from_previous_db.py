import sqlite3
from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
import itertools
import pymongo
from resolution.validation.google_scholar import parse_google_scholar_name
from resolution.parse.parse import remove_stop_words

''' Parse 24,763 google scholar articles from previous sqlite3 db '''

table    = 'google_scholar_new'
all_rows = 'SELECT * from {}'


def expand_author_row(row, articles):
    failures = 0
    _, ids, full_name, scholar_id = row
    name = parse_google_scholar_name(full_name)
    # pprint(name)
    mongo_ids = []
    titles    = []
    dois      = []
    for doi in ids.split(','):
        article = articles.find_one({'front.article-meta.article-id.#text' : doi})
        if article is not None:
            mongo_ids.append(article['_id'])
            titles.append(article['title'])
            # pprint(article)
        else: # :(
            mongo_ids.append(None)
            titles.append(None)
            failures += 1
        dois.append(doi)
    # pprint(dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids))
    return failures, dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids)

def run():
    mongo_client = MongoClient('localhost', 27017)

    sql_client   = sqlite3.connect('database/jstor-resolution.db')
    sql_cursor   = sql_client.cursor()

    jstor_database    = mongo_client.jstor_database
    mongo_client.validation.drop_collection('google_scholar_dois')
    scholar           = mongo_client.validation.google_scholar_dois
    articles          = jstor_database.articles
    articles.create_index([('front.article-meta.article-id.#text', pymongo.TEXT)])

    failures = 0

    sql_cursor.execute(all_rows.format(table))
    for row in sql_cursor.fetchall():
        print(f'{failures} failures')
        new_failures, doc = expand_author_row(row, articles)
        failures += new_failures
        scholar.insert_one(doc)

