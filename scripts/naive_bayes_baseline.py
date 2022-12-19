from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

import sklearn
import pandas as pd

from sklearn.naive_bayes import CategoricalNB

import dill as pickle

from resolution.baselines.utils import *

def run():
    client    = MongoClient('localhost', 27017)

    training = load_training('/workspace/JSTOR_pairwise.csv.gz')

    features = [f'x{i}' for i in range(1, 11)]

    clf = CategoricalNB()
    clf.fit(training[features], training['label'])
    binary = Binary(pickle.dumps(clf), subtype=128)

    client.baselines.classifiers.delete_many(dict(name='naive_bayes'))
    client.baselines.classifiers.insert_one(dict(name='naive_bayes', binary=binary))

