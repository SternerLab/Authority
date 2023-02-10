
import pymongo
from pathlib import Path
from rich.pretty import pprint
from rich.progress import track
from rich import print

import csv
import gzip

from resolution.baselines.training_data import *

def run():
    client = get_client('mongo_credentials.json', local=True)
    articles = client.jstor_database.articles
    features = client.features

    full = False
    headers, ext = get_headers_and_ext(full=full)
    frequency_lookup = make_frequency_lookup(path='data/names.csv')

    pairwise_path = Path(f'/workspace/JSTOR_pairwise{ext}.csv.gz')
    with gzip.open(pairwise_path, 'wt') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        for ref_key in features.list_collection_names():
            if 'match' not in ref_key:
                continue
            is_positive = 'non_match' not in ref_key
            to_table(articles, frequency_lookup, features[ref_key], ref_key, is_positive, writer, full)
