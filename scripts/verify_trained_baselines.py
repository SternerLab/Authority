
from pathlib import Path

import sklearn
import pandas as pd
import numpy  as np

from resolution.baselines.utils import *
from resolution.database.client import get_client

from sklearn.naive_bayes import CategoricalNB
from xgboost import XGBClassifier


def run():
    client = get_client('mongo_credentials.json', local=True)

    for classifier in client.baselines.classifiers.find():
        print(classifier['name'])
