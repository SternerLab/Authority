from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
import requests
import json

from authority.validation.biodiversity import lookup, parse
from concurrent.futures import ThreadPoolExecutor as Pool

import itertools
import functools

def parse_bhl_article(article, key=None, bhl=None):
    print(article['title'])
    for author in article['authors']:
        if bhl is not None:
            if bhl.find_one({'author.key' : author['key']}) is None:
                continue
        print(author['key'])
        i = 0
        for result in lookup(author['full'], key=key):
            i += len(set(result['titles']))
            pprint(result['author_id'])
            pprint(result['author'])
            pprint(result['titles'])
            yield result
        print(f'found {i} BHL articles for search {author["full"]}')

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    collect = jstor_database.articles
    n = collect.count_documents({})

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl
    bhl = client.validation.bhl

    with open('bhl_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    api_key = credentials['api_key']

    with client.start_session(causal_consistency=True) as session:
        tracked_cursor = track(collect.find(no_cursor_timeout=True, session=session), total=n)
        for article in tracked_cursor:
            to_insert = list(parse_bhl_article(article, key=api_key, bhl=bhl))
            if len(to_insert) > 0:
                print(f'BHL resolved {len(to_insert)} JSTOR articles from article:\n {article["title"]} with authors {[a["key"] for a in article["authors"]]}')
                bhl.insert_many(to_insert)
