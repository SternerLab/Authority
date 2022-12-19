from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

import pandas as pd
import dill as pickle

from xgboost import XGBClassifier

def run():
    client    = MongoClient('localhost', 27017)

    df = pd.read_csv('/workspace/JSTOR_pairwise.csv.gz', compression='gzip')
    df = df.sample(frac=1).reset_index(drop=True)
    df.dropna(inplace=True)
    features = [f'x{i}' for i in range(1, 11)]

    xgb = XGBClassifier(max_depth=3, learning_rate=1)
    xgb.fit(df[features], df['label'])
    binary = Binary(pickle.dumps(xgb), subtype=128)

    client.baselines.classifiers.insert_one(dict(name='xgboost', binary=binary))

