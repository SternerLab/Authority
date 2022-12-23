from pymongo import MongoClient
import pymongo
from pathlib import Path
from rich.pretty import pprint
from rich.progress import track
from rich import print

import logging
log = logging.getLogger('rich')

import itertools
import scipy
import numpy as np
import pandas as pd
import csv
import gzip

from resolution.validation.self_citations import SelfCitationResolver

from .create_heuristic_training_data import (to_table_generator,
                                             to_table, get_headers_and_ext)

def find_self_citation_labeled_pairs(client, features, subsets, filn):
    self_citations = SelfCitationResolver(client, 'self_citations')
    self_citations.build_cache()

    cache = dict()
    for group in track(subsets.find(),
                       description='Building author key resolution cache',
                       total=subsets.count_documents({})):
        fi = group['_id']['first_initial']
        ln = group['_id']['last']
        key = f'{fi}{ln}'
        labels = self_citations.group_resolve(group)
        cache[key] = labels, group['_id']

    for cluster in track(filn.find(), description='Finding labeled pairs',
                         total=filn.count_documents({})):
        pair   = cluster['pair']
        key    = pair[0]['authors']['key']
        labels, group_id = cache[key]
        a, b   = (str(p['ids']) for p in pair)
        if a in labels and b in labels and labels[a] == labels[b]:
            yield group_id, cluster

def run():
    client = MongoClient('localhost', 27017)
    articles = client.jstor_database.articles
    subsets  = client.reference_sets['first_initial_last_name']
    features = client.features
    filn     = features['first_initial_last_name']
    full = True

    headers, ext = get_headers_and_ext(full=full)

    pairwise_path = Path(f'/workspace/JSTOR_self_citations_pairwise{ext}.csv.gz')
    with gzip.open(pairwise_path, 'wt') as outfile:
    # with gzip.open(pairwise_path, 'at') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)

        # First write the positive labels from self citations
        log.info('Creating tabular self citation match data')
        pair_gen = find_self_citation_labeled_pairs(client, features, subsets, filn)
        pair_docs = (c for g, c in pair_gen)
        to_table_generator(articles, pair_docs, True, writer, full)

        log.info('Creating tabular non-match training data')

        # Then write only the non-match data to csv
        ref_key = 'first_name_non_match'
        to_table(articles, features[ref_key], ref_key, False, writer, full)
