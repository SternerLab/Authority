from pymongo import MongoClient
import pymongo
from pathlib import Path
from rich.pretty import pprint
from rich.progress import track
from rich import print

import logging
log = logging.getLogger('rich')

import itertools
import scipy
import numpy as np
import pandas as pd
import csv
import gzip

from resolution.validation.self_citations import SelfCitationResolver
from .create_self_citation_training_data import *


def run():
    client = MongoClient('localhost', 27017)
    articles          = client.jstor_database.articles
    subsets           = client.reference_sets['first_initial_last_name']
    features          = client.features
    filn              = features['first_initial_last_name']
    client.reference_sets_pairs.drop_collection('self_citations')
    client.reference_sets_lookup.drop_collection('self_citations')
    self_cites        = client.reference_sets_pairs['self_citations']
    self_cites_lookup = client.reference_sets_lookup['self_citations']

    gen = find_self_citation_labeled_pairs(client, features, subsets, filn)
    for group_id, pair in gen:
        result = self_cites.insert_one(pair)
        self_cites_lookup.update_one({'group_id' : group_id},
                                     {'$push' : {'pair_ids' : result.inserted_id}},
                                     upsert=True)


