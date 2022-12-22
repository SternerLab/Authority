from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

from pathlib import Path

import sklearn
import pandas as pd
import numpy  as np

from sklearn.naive_bayes import CategoricalNB

import dill as pickle

from resolution.baselines.utils import *

def run():
    client    = MongoClient('localhost', 27017)
    np.random.seed(2022)

    path = Path('/workspace/JSTOR_self_citations_pairwise.csv.gz')
    # path = Path('/workspace/JSTOR_pairwise.csv.gz')
    data = load_shuffle(path)
    print(data)

    train_classifier(client, CategoricalNB, 'naive_bayes', data)
