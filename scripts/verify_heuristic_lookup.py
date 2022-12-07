from pymongo import MongoClient
from rich.pretty import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

def run():
    client = MongoClient('localhost', 27017)
    for ref_key in ['mesh_coauthor_match', 'name_match']:
        lookup = client.reference_sets_group_lookup[ref_key]
        doc = lookup.find_one()
        pprint(doc)
