from pymongo import MongoClient
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

import traceback

def _mongodb_segfault_handler(signum, frame):
    # This is likely from a corrupted binary or document in mondodb, which is hard to isolate
    print(f'MongoDB encountered a segfault while validating:')
    traceback.print_stack(frame)

signal.signal(signal.SIGSEGV, _mongodb_segfault_handler)
# os.kill(os.getpid(), signal.SIGSEGV) # To test the segfault handler

def run():
    log = logging.getLogger('rich')
    log.setLevel(logging.DEBUG)
    # First connect to MongoDB and setup the databases and collections in it
    client   = MongoClient('localhost', 27017)
    articles = client.jstor_database.articles

    # Load the available validation sources and cache them in memory
    # source_names = possible_sources # To use all

    source_names = ['biodiversity', 'google_scholar', 'self_citations', 'orcid',
                    'merge_heuristic', 'split_heuristic', 'full_name_heuristic',
                    'mesh_coauthor_heuristic', 'name_heuristic']
    sources = load_sources(client, source_names)

    # Controls which clusters we are validating
    query = {}
    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'afton'}}
    # query = {'group_id.first_initial' : 'a'}
    # query = {'group_id.first_initial' : 'b'}
    # query = {'group_id.last' : 'smith'}
    # query = {'group_id.last' : 'johnson'}
    # query = {'group_id' : {'first_initial' : 'd', 'last' : 'johnson'}}
    # query = {'group_id' : {'first_initial' : 'l', 'last' : 'smith'}}
    # query = {'group_id' : {'first_initial' : 'c', 'last' : 'miller'}}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'hedenström'}}
    # query = {'group_id' : {'first_initial' : 'a', 'last': 'smith'}}
    query = {'group_id' : {'first_initial' : 'j', 'last': 'smith'}}

    # authority_self_citations
    # naive_bayes
    # naive_bayes_agglomerative
    # authority_clipped
    # first_initial_last_name
    # xgboost_agglomerative
    # naive_bayes_components
    # authority_mixed
    # authority
    # xgboost
    # xgboost_components
    # authority_no_correction

    prediction_sources = ['authority', 'naive_bayes', 'xgboost', #'authority_mixed',
                          'authority_clipped', #'authority_no_correction',
                          'scibert_clustering',  'authority_no_correction_robust',
                          'authority_mixed_no_correction',
                          #'authority_legacy_ratios',
                          'authority_torvik_ratios']
    # prediction_sources = ['authority', 'naive_bayes_agglomerative', 'xgboost_agglomerative']
    predictions = {k : client.inferred[k] for k in prediction_sources}
    predictions['authority_legacy'] = client.previous_inferred.previous_inferred
    stream = validate_all(client, predictions, query, sources)

    first = next(stream)

    # No memory issues from this method :)
    with open('data/resolution_validation_metrics.csv', 'w') as outfile:
        dict_writer = csv.DictWriter(outfile, first.keys())
        dict_writer.writeheader()
        dict_writer.writerows([first])
        dict_writer.writerows(stream)
