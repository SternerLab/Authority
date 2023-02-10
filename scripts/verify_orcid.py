
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from functools import partial
import functools
import itertools
import requests
import pymongo
import pandas as pd
import json

from resolution.validation.orcid import *
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    articles         = client.jstor_database.articles

    orcid_collection = client.validation.orcid
    orcid_lookup     = client.validation.orcid_lookup

    print(f'Orcid clusters')
    for item in orcid_collection.find():
        print(item)

    for doc in orcid_lookup.find():
        for title, (orcid_id, mongo_id, doi) in doc['lookup'].items():
            print(f'{doc["key"]}-{orcid_id}, {mongo_id}, {doi}: {title}')
