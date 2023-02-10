
from rich.pretty import pprint
from rich import print
import dill as pickle
import pandas as pd
import logging
import pymongo
import signal
import csv
import os

from bson.objectid import ObjectId

from rich.progress import track

from resolution.validation.metrics import *
from resolution.validation.validate import validate_all, load_sources, possible_sources
from resolution.database.client import get_client

import traceback

def run():
    log = logging.getLogger('rich')
    log.setLevel(logging.DEBUG)
    client = get_client('mongo_credentials.json', local=True)
    articles = client.jstor_database.articles

    prediction_sources = ['naive_bayes', 'xgboost']
    predictions = {k : client.inferred[k] for k in prediction_sources}
    predictions['authority_legacy'] = client.previous_inferred.previous_inferred

    query = {'group_id.first_initial' : 'a'}
    for i, (name, inferred) in enumerate(predictions.items()):
        inferred_size = inferred.count_documents({})
        query_str = str(query).replace('group_id', '')
        log.info(f'Validating {name}')
        log.info(f'    query {query_str} -> {inferred_size} docs')
        print(inferred.find_one(query), flush=True)
        for doc in inferred.find():
            print(doc)
        for i, cluster in track(enumerate(inferred.find(query)), total=inferred_size,
                                description='Creating validation generator'):
            log.info(f'Cluster {i:3}: {cluster}')
            print(cluster, flush=True)
