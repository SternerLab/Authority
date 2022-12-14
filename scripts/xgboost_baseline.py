from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd

from xgboost import XGBClassifier

def run():
    df = pd.read_csv('/workspace/JSTOR_pairwise.csv.gz', compression='gzip')
    df.dropna()
    df = df.sample(frac=1).reset_index(drop=True)
    le = LabelEncoder()

    train, test = train_test_split(df, test_size=0.3)
    print(train.head(4))
    features = [f'x{i}' for i in range(1, 11)]
    train_in, train_labels = train[features], train['label']
    train_labels = le.fit_transform(train_labels)

    xgb = XGBClassifier(max_depth=3, learning_rate=1)# , objective='binary')
    xgb.fit(train_in, train_labels)
    print(xgb.score(train_in, train_labels))

    test_in, test_labels = test[features], test['label']
    test_labels = le.fit_transform(train_labels)
    print(xgb.score(test_in, test_labels))
