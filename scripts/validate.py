from pymongo import MongoClient
from rich.pretty import pprint
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
    source_names = ['google_scholar',  # 'self_citations',
                    # 'merge_heuristic', 'split_heuristic',
                    'meshcoauthor_heuristic', 'name_heuristic']
    sources = load_sources(client, source_names)

    # Controls which clusters we are validating
    query = {}

    # Finally, validate!
    new_clusters = client.inferred['first_initial_last_name']
    new_df = validate_clusters(new_clusters, query, sources)
    new_df['year'] = 2022
    # To validate Manuha's clusters
    old_clusters = client.previous_inferred.previous_inferred
    old_df = validate_clusters(new_clusters, query, sources)
    old_df['year'] = 2021

    df = pd.concat([new_df, old_df])
    df.to_csv('data/authority_validation_metrics.csv')
