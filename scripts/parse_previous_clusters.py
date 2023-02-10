import sqlite3

from rich.pretty import pprint
from rich.progress import track
from rich import print
import itertools
import pymongo
import json
from resolution.validation.google_scholar import parse_google_scholar_name
from resolution.parse.parse import remove_stop_words
from resolution.database.client import get_client


table    = 'clusters_all'
all_rows = 'SELECT * from {}'
show_columns = 'PRAGMA table_info({});'

# │   'front': {
# │   │   'article-meta': {
# │   │   │   'article-id': {
# │   │   │   │   '#text': '23651754'

def resolve(aid, articles):
    result = articles.find_one({'front.article-meta.article-id.#text' : aid})
    if result is None:
        return None
    else:
        return str(result['_id'])

def expand_cluster(row, articles):
    first_initial_last_name, total_records, clusters, total_clusters, authors, author_count = row
    # Why are they stored like this?
    clusters = clusters.replace('\'', '').replace('"', '').replace('[', '').replace(']', '').split(',')
    clusters = [[aid.strip() for aid in c.split(';')] for c in clusters]
    resolved_clusters = [[resolve(aid, articles) for aid in aids] for aids in clusters]
    resolved_clusters = [[aid for aid in aids if aid is not None] for aids in resolved_clusters]
    last, fi = first_initial_last_name.split('_')
    key = f'{fi.lower()}{last.lower()}'
    return dict(group_id=dict(first_initial=fi.lower(), last=last.lower()),
                key=key,
                cluster_labels={k : i for i, cluster in enumerate(resolved_clusters) for k in cluster})

def generator(sql_cursor, articles):
    total = sql_cursor.execute(f'SELECT COUNT() FROM {table}').fetchone()[0]
    sql_cursor.execute(show_columns.format(table))
    print(sql_cursor.fetchall())
    sql_cursor.execute(all_rows.format(table))
    for row in track(sql_cursor.fetchall(), total=total, description='Parsing..'):
        yield expand_cluster(row, articles)

def run():
    mongo_get_client('mongo_credentials.json', local=True)

    sql_client   = sqlite3.connect('database/jstor-authority.db')
    sql_cursor   = sql_client.cursor()

    jstor_database    = mongo_client.jstor_database
    articles          = jstor_database.articles
    articles.create_index('front.article-meta.article-id.#text')

    mongo_client.drop_database('previous_inferred')
    clusters          = mongo_client.previous_inferred.previous_inferred

    clusters.insert_many(generator(sql_cursor, articles))

