from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import dill as pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from resolution.validation.metrics import *
from resolution.validation.self_citations import resolve, make_contiguous, build_self_citation_cache

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['first_initial_last_name']
    for i, cluster in enumerate(inferred_blocks.find()):
        print(cluster)
        break
    print(inferred_blocks.count_documents({}))
