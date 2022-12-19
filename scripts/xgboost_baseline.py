from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

import pandas as pd
import dill as pickle

from xgboost import XGBClassifier

from resolution.baselines.utils import *

def run():
    client    = MongoClient('localhost', 27017)
    training = load_training('/workspace/JSTOR_pairwise.csv.gz')
    features = [f'x{i}' for i in range(1, 11)]

    xgb = XGBClassifier(max_depth=3, learning_rate=1)
    xgb.fit(training[features], training['label'])
    binary = Binary(pickle.dumps(xgb), subtype=128)

    client.baselines.classifiers.delete_many(dict(name='xgboost'))
    client.baselines.classifiers.insert_one(dict(name='xgboost', binary=binary))

