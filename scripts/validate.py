from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from authority.validation.metrics import *
from authority.validation.validate import validate, load_sources, possible_sources

def run():
    # First connect to MongoDB and setup the databases and collections in it
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['first_initial_last_name']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    # Load the available validation sources and cache them in memory
    # source_names = possible_sources # To use all
    source_names = ['self_citations']
    sources = load_sources(client, source_names)

    # Finally, validate!
    cluster = None # TODO for testing
    validate(cluster, sources)
