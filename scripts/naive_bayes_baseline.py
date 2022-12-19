from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

import sklearn
from sklearn.model_selection import train_test_split
import pandas as pd

from sklearn.naive_bayes import CategoricalNB

import dill as pickle

def run():
    client    = MongoClient('localhost', 27017)

    df = pd.read_csv('/workspace/JSTOR_pairwise.csv.gz', compression='gzip')
    df = df.sample(frac=1).reset_index(drop=True)
    df.dropna(inplace=True)
    features = [f'x{i}' for i in range(1, 11)]

    clf = CategoricalNB()
    clf.fit(df[features], df['label'])
    binary = Binary(pickle.dumps(clf), subtype=128)

    client.baselines.classifiers.insert_one(dict(name='naive_bayes', binary=binary))

