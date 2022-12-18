from pymongo import MongoClient
from bson.son import SON
from bson.binary import Binary

from rich.pretty import pprint
from rich.progress import track

import sklearn
from sklearn.model_selection import train_test_split
import pandas as pd

from sklearn.naive_bayes import CategoricalNB

def run():
    df = pd.read_csv('/workspace/JSTOR_pairwise.csv.gz', compression='gzip')
    df = df.sample(frac=1).reset_index(drop=True)
    df.dropna(inplace=True)
    train, test = train_test_split(df, test_size=0.3)
    print(train.head(4))
    features = [f'x{i}' for i in range(1, 11)]
    train_in, train_labels = train[features], train['label']

    clf = CategoricalNB()
    clf.fit(train_in, train_labels)
    print(clf.score(train_in, train_labels))

    test_in, test_labels = test[features], test['label']
    print(clf.score(test_in, test_labels))
    rs_binary = Binary(pickle.dumps(rs), subtype=128)
