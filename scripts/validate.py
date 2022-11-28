from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from authority.validation.metrics import *
from authority.validation.validate import validate_clusters, load_sources, possible_sources

def run():
    # First connect to MongoDB and setup the databases and collections in it
    client   = MongoClient('localhost', 27017)
    articles = client.jstor_database.articles

    # Load the available validation sources and cache them in memory
    # source_names = possible_sources # To use all
    source_names = ['self_citations']
    sources = load_sources(client, source_names)

    # Controls which clusters we are validating
    query = {}

    # Finally, validate!
    clusters = client.inferred['first_initial_last_name']
    # To validate Manuha's clusters
    # clusters = client.previous_inferred.previous_inferred

    df = validate_clusters(clusters, query, sources)
    df.to_csv('data/authority_validation_metrics.csv')
