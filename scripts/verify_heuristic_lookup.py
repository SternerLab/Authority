
from rich.pretty import pprint
from rich import print
import dill as pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId
from resolution.database.client import get_client

def run():
    get_client('mongo_credentials.json', local=False)
    for ref_key in ['mesh_coauthor_match', 'name_match']:
        lookup = client.reference_sets_group_lookup[ref_key]
        doc = lookup.find_one()
        pprint(doc)
