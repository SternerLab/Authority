
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

from resolution.validation.metrics import *
from resolution.validation.validate import validate_all, load_sources, possible_sources
from resolution.database.client import get_client

import traceback

def _mongodb_segfault_handler(signum, frame):
    # (OLD): Only occurred once, after a database corruption (yikes!)
    # This is likely from a corrupted binary or document in mondodb, which is hard to isolate
    print(f'MongoDB encountered a segfault while validating:')
    traceback.print_stack(frame)

signal.signal(signal.SIGSEGV, _mongodb_segfault_handler)
# os.kill(os.getpid(), signal.SIGSEGV) # To test the segfault handler

def get_common_names(n=200):
    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)
    common_names = list(set(names['last'].iloc[:n]))
    return common_names

def run():
    log = logging.getLogger('rich')
    log.setLevel(logging.DEBUG)
    # First connect to MongoDB and setup the databases and collections in it
    client = get_client('mongo_credentials.json', local=True)
    articles = client.jstor_database.articles

    # Load the available validation sources and cache them in memory
    # source_names = possible_sources # To use all

    source_names = ['biodiversity', 'google_scholar',
                    'self_citations',
                    'orcid',
                    'merge_heuristic', 'split_heuristic', 'full_name_heuristic',
                    'mesh_coauthor_heuristic', 'name_heuristic']
    sources = load_sources(client, source_names)

    common_names = get_common_names()
    print(common_names)

    # Controls which clusters we are validating
    # query = {}
    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'afton'}}
    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'baker'}}
    # query = {'group_id.first_initial' : 'b'}
    # query = {'group_id.last' : 'smith'}

    # query = {'group_id.first_initial' : { '$in' : list('abcdefg')}}

    # query = {'group_id.last' : {'$in' : common_names}}
    # query = {'group_id.last' : {'$in' : ['smith']}}

    # query = {'group_id.last' : 'johnson'}
    # query = {'group_id' : {'first_initial' : 'd', 'last' : 'johnson'}}
    # query = {'group_id' : {'first_initial' : 'l', 'last' : 'smith'}}
    # query = {'group_id' : {'first_initial' : 'c', 'last' : 'miller'}}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'hedenström'}}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'smith'}}
    # query = {'group_id' : {'first_initial' : 'j', 'last': 'smith'}}

    prediction_sources = [
                          'authority', 'scibert_clustering',
                          'authority_clipped',
                          'authority_no_correction',
                          'authority_mixed',
                          'authority_self',
                          'authority_torvik_ratios',
                          'authority_no_correction_robust',
                          'authority_reversed']
    for classifier in ['naive_bayes', 'xgboost']:
        for ext in ['_self_citations', '_authority_heuristics',
                    '_heuristics', '_heuristics_balanced',
                    '_both', '_both_balanced']:
            for cluster_method in ['', '_agglomerative']:
                prediction_sources.append(
                        f'{classifier}{ext}{cluster_method}')
    print(f'Prediction sources:')
    pprint(prediction_sources)
    # prediction_sources = ['naive_bayes', 'xgboost', 'authority', 'authority_clipped']
    predictions = {k : client.inferred[k] for k in prediction_sources}
    predictions['authority_legacy'] = client.previous_inferred.previous_inferred

    headers = False
    with open('data/resolution_validation_metrics.csv', 'w') as outfile:
        for initial in 'abcdefghijklmnopqrstuvwxyz':
            print(f'STARTING ON INITIAL: {initial}')
            query = {'group_id.first_initial' : initial}

            stream = validate_all(client, predictions, query, sources)
            first = next(stream)
            dict_writer = csv.DictWriter(outfile, first.keys())

            # No memory issues from this method :)
            if not headers:
                dict_writer.writeheader()
                headers = True
            dict_writer.writerows([first])
            dict_writer.writerows(stream)
