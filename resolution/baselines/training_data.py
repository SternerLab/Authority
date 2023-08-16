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

import logging
log = logging.getLogger('rich')

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

def make_frequency_lookup(path='data/names.csv'):
    frequency_lookup = dict()
    names = pd.read_csv(path)
    for a in names.itertuples():
        frequency_lookup[a.key] = a.count
    return frequency_lookup

def to_table_generator(articles, frequency_lookup, generator, label, writer, full):
    for doc in generator:
        key = doc['pair'][0]['authors']['key']
        frequency = frequency_lookup[key]
        features = list(doc['features'].values())
        if full:
            features = fetch_full_features(doc, articles) + features
        ids = [str(p['ids']) for p in doc['pair']]
        writer.writerow(ids + [frequency] + features + [label])

def to_table(articles, frequency_lookup, collection, ref_key, label, writer, full):
    generator = track(collection.find(), total=collection.count_documents({}),
                      description=f'Converting {ref_key} to table')
    to_table_generator(articles, frequency_lookup, generator, label, writer, full)

def get_headers_and_ext(full=False):
    headers = ['id_0', 'id_1'] + ['frequency'] + [f'x{i}' for i in range(1, 11)] + ['label']
    if full:
        ext = '_full'
        fields = [f'{f}_{i}' for f in __fields for i in range(2)]
        headers = fields + headers
    else:
        ext = ''
    return headers, ext
