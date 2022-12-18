from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
from rich.progress import Progress

from functools import partial
import functools
import itertools
import requests
import pymongo
import pandas as pd
import json

from .download_bhl import parse_bhl_article

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles = jstor_database.articles
    n = articles.count_documents({})

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl
    bhl = client.validation.bhl

    with open('bhl_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    api_key = credentials['api_key']

    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)

    best_resolutions = dict()

    with client.start_session(causal_consistency=True) as session:
        for key in names['key']:
            query = {'authors.key' : key}
            total = 0
            for article in articles.find(query, no_cursor_timeout=True, session=session):
                insertions = list(parse_bhl_article(article, key=api_key))
                total += len(insertions)
                if len(insertions) > 0:
                    break
                    # bhl.insert_many(insertions)
            if total > 1:
                best_resolutions[key] = total
            print(f'Resolved {total} articles for key {key}')

            print(best_resolutions)

