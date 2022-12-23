from pymongo import MongoClient
from pathlib import Path

import sklearn
import pandas as pd
import numpy  as np

from xgboost import XGBClassifier

from resolution.baselines.utils import *

def run():
    client    = MongoClient('localhost', 27017)
    np.random.seed(2022)

    self_cites = Path('/workspace/JSTOR_self_citations_pairwise.csv.gz')
    heuristic  = Path('/workspace/JSTOR_pairwise.csv.gz')
    self_cites = load_shuffle(self_cites)
    heuristic  = load_shuffle(heuristic)

    data = pd.concat((self_cites, heuristic))
    # print(data)
    train_classifier(client, XGBClassifier, 'xgboost', data)
