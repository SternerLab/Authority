import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track, Progress
from bson.son import SON
import itertools
from pathlib import Path

def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    sets         = client.reference_sets
    pairs        = client.reference_sets_pairs
    group_lookup = client.reference_sets_group_lookup

    names_file = Path('names.csv')
    if not names_file.is_file():
        names = []
        total = sets['first_initial_last_name'].count_documents({})
        for doc in track(sets['first_initial_last_name'].find(), total=total):
            gid = doc['_id']
            key = gid['first_initial'] + gid['last']
            print(key, doc['count'])
            name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
            names.append(dict(key=key, count=doc['count'], name=name, **doc['_id']))

        df = pd.DataFrame(names)
        df.to_csv('names.csv')

    val_df = pd.read_csv('authority_validation_metrics.csv')
    val_df.fillna(0, inplace=True)

    val_df['frequency'] = 0
    names_df = pd.read_csv('names.csv')

    for tup in track(names_df.itertuples(), total=names_df.shape[0]):
        print(tup.name)
        queried = val_df[val_df.name == tup.name]
        if queried.empty:
            continue
        queried['frequency'] = tup.count
    val_df.to_csv('composite.csv')
