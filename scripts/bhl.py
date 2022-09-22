from pymongo import MongoClient
from rich.pretty   import pprint
from rich.progress import track
import requests
import json

from authority.validation.biodiversity_library import lookup, parse
from concurrent.futures import ThreadPoolExecutor as Pool

import itertools
import functools

def process_article(article, key=None):
    print(article['title'])
    for author in article['authors']:
        print(author['key'])
        for result in lookup(author['full'], key=key):
            pprint(result['author_id'])
            pprint(result['author'])
            pprint(result['titles'])
            yield result

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    collect = jstor_database.articles
    n = collect.count_documents({})

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl

    with open('bhl_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    api_key = credentials['api_key']

    threads    = 2
    batch_size = 8

    tracked_cursor = track(collect.find(), total=n)
    mapped_func    = functools.partial(process_article, key=api_key)
    with Pool(max_workers=threads) as pool:
        while True:
            batch = list(itertools.islice(tracked_cursor, batch_size))
            if len(batch) == 0:
                break
            for results in pool.map(mapped_func, batch):
                for result in results:
                    bhl.insert_one(result)
