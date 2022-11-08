import sqlite3
from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
import itertools
import pymongo
import json
from authority.validation.google_scholar import parse_google_scholar_name
from authority.parse.parse import remove_stop_words


table    = 'clusters_all'
all_rows = 'SELECT * from {}'
show_columns = 'PRAGMA table_info({});'

# │   'front': {
# │   │   'article-meta': {
# │   │   │   'article-id': {
# │   │   │   │   '#text': '23651754'

def resolve(aid, articles):
    return str(articles.find_one({'front.article-meta.article-id.#text' : aid})['_id'])

def expand_cluster(row, articles):
    first_initial_last_name, total_records, clusters, total_clusters, authors, author_count = row
    print(first_initial_last_name)
    # Why are they stored like thi are they stored like thiss?
    clusters = clusters.replace('\'', '').replace('"', '').replace('[', '').replace(']', '').split(',')
    clusters = [[aid.strip() for aid in c.split(';')] for c in clusters]
    print(clusters)
    resolved_clusters = [[resolve(aid, articles) for aid in aids] for aids in clusters]
    return resolved_clusters

# def expand_author_row(row, articles):
#     _, ids, full_name, scholar_id = row
#     name = parse_google_scholar_name(full_name)
#     pprint(name)
#     mongo_ids = []
#     titles    = []
#     dois      = []
#     for doi in ids.split(','):
#         article = articles.find_one({'front.article-meta.article-id.#text' : doi})
#         if article is not None:
#             mongo_ids.append(article['_id'])
#             titles.append(article['title'])
#         else: # :(
#             mongo_ids.append(None)
#             titles.append(None)
#         dois.append(doi)
#     pprint(dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids))
#     return dict(author=name, title=titles, dois=dois, mongo_ids=mongo_ids)

def run():
    mongo_client = MongoClient('localhost', 27017)

    sql_client   = sqlite3.connect('database/jstor-authority.db')
    sql_cursor   = sql_client.cursor()

    jstor_database    = mongo_client.jstor_database
    articles          = jstor_database.articles
    articles.create_index('front.article-meta.article-id.#text')

    clusters          = mongo_client.previous_inferred.previous_inferred

    sql_cursor.execute(show_columns.format(table))
    print(sql_cursor.fetchall())
    sql_cursor.execute(all_rows.format(table))
    for row in sql_cursor.fetchall():
        print(row)
        print(expand_cluster(row, articles))
        # clusters.insert_one(expand_cluster(row))
        break

