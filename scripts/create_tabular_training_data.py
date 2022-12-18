from pymongo import MongoClient
import pymongo
from pathlib import Path
from rich.pretty import pprint
from rich.progress import track
from rich import print

import itertools
import scipy
import numpy as np
import pandas as pd
import csv
import gzip

__fields = ['title', 'abstract', 'journal', 'mesh', 'year', 'language', 'authors.first', 'authors.middle_initial', 'authors.last']

def fetch_full_features(pair, articles):
    features = []
    ids = [p['ids'] for p in pair['pair']]
    for i in ids:
        full = articles.find_one({'_id' : i})
        for field in __fields:
            value = full
            for el in field.split('.'):
                value = value[el]
                # Could be cleaner, but it is correct :)
                if 'authors' in field and isinstance(value, list):
                    value = value[0]
            if field == 'language':
                value = '-'.join(value)
            features.append(value)
    return features

def to_table(articles, collection, ref_key, label, writer, full):
    description = f'Converting {ref_key} to table'
    for doc in track(collection.find(),
                     total=collection.count_documents({}),
                     description=description):
        features = list(doc['features'].values())
        if full:
            features = fetch_full_features(doc, articles) + features
        ids = [str(p['ids']) for p in doc['pair']]
        writer.writerow(ids + features + [label])

def run():
    client = MongoClient('localhost', 27017)
    articles = client.jstor_database.articles
    features = client.features

    # full = True
    full = False

    headers = ['id_0', 'id_1'] + [f'x{i}' for i in range(1, 11)] + ['label']
    if full:
        ext = '_full'
        fields = [f'{f}_{i}' for f in __fields for i in range(2)]
        headers = fields + headers
    else:
        ext = ''

    pairwise_path = Path(f'/workspace/JSTOR_pairwise{ext}.csv.gz')
    with gzip.open(pairwise_path, 'wt') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        for ref_key in features.list_collection_names():
            if 'match' not in ref_key:
                continue
            is_positive = 'non_match' not in ref_key
            to_table(articles, features[ref_key], ref_key, is_positive, writer, full)


