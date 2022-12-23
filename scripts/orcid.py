from pymongo import MongoClient
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from functools import partial
import functools
import itertools
import requests
import pymongo
import pandas as pd
import json

from resolution.validation.orcid import *

def run():
    client           = MongoClient('localhost', 27017)
    articles         = client.jstor_database.articles

    client.validation.drop_collection('orcid')
    client.validation.drop_collection('orcid_lookup')

    orcid_collection = client.validation.orcid
    orcid_lookup     = client.validation.orcid_lookup

    filn = client.reference_sets.first_initial_last_name

    titles_cache = dict()
    q = {'_id.last' : 'smith'}
    for group in track(filn.find(q), total=filn.count_documents({}),
                       description='Building title cache'):
        gid    = group['_id']
        key    = f'{gid["first_initial"]}{gid["last"]}'
        titles = dict()
        for doc in group['group']:
            titles[doc['title']] = str(doc['ids'])
        titles_cache[key] = titles

    orcid_scraper    = OrcidScraper('orcid_credentials.json')

    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)
    best_resolutions = dict()
    with client.start_session(causal_consistency=True) as session:
        for a in names.itertuples():
            titles = titles_cache[a.key]
            lookup, clusters = orcid_scraper.resolve(a, titles)
            pprint(lookup)
            pprint(clusters)
            orcid_collection.insert_one(dict(author=dict(key=a.key, full_name=a.name, last=a.last, first_initial=a.first_initial),
                                             mongo_ids=clusters))
            orcid_lookup.insert_one(dict(key=a.key, lookup=lookup))
            1/0
