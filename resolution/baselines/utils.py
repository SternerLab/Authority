import pandas as pd
from sklearn.model_selection import train_test_split
from bson.binary import Binary
import logging
import dill as pickle

log = logging.getLogger('rich')

def load_shuffle(path):
    df = pd.read_csv(path, compression='gzip')
    df = df.sample(frac=1).reset_index(drop=True)
    df.dropna(inplace=True)
    log.info(f'Successfully loaded {path}:')
    pos = len(df[df["label"] == True])
    neg = len(df[df["label"] == False])
    log.info(f'positive pairs: {pos} ({pos/(pos+neg):.2%})')
    log.info(f'negative pairs: {neg} ({neg/(pos+neg):.2%})')
    return df

def train_classifier(client, Constructor, name, data, *args, **kwargs):
    train, test = train_test_split(data, test_size=0.2, random_state=2022)

    features = [f'x{i}' for i in range(1, 11)]
    # First, fit a classifier on train only and report evaluation
    log.info(f'Training {name} on preliminary 80/20 test-train split...')
    clf = Constructor(*args, **kwargs)
    clf.fit(train[features], train['label'])
    for k, d in (('train', train), ('test', test)):
        acc = clf.score(d[features], d['label'])
        log.info(f'{name} achieved {acc:.2%} {k} accuracy')

    log.info('Training on whole dataset...')
    clf = Constructor(*args, **kwargs) # Reset!
    clf.fit(data[features], data['label'])
    acc = clf.score(data[features], data['label'])
    log.info(f'{name} achieved training accuracy of {acc:.2%}')

    log.info(f'Uploading trained {name} model to database')
    binary = Binary(pickle.dumps(clf), subtype=128)

    client.baselines.classifiers.delete_many(dict(name=name))
    client.baselines.classifiers.insert_one(dict(name=name, binary=binary))
