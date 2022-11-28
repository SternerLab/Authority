from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from .metrics import *
from .self_citations import SelfCitationResolver
from .google_scholar import GoogleScholarResolver
from .biodiversity   import BiodiversityResolver

possible_sources = ['self_citations', 'google_scholar', 'biodiversity', 'manual']

def load_sources(client, source_names):
    ''' Resolve multiple sources to their reference clusters '''
    sources = dict()
    for source_name in source_names:
        match source_name:
            case 'self_citations':
                sources[source_name] = SelfCitationResolver(client, source_name)
            case 'google_scholar':
                sources[source_name] = GoogleScholarResolver(client, source_name)
            case 'biodiversity':
                sources[source_name] = BiodiversityResolver(client, source_name)
            case 'manual':
                sources[source_name] = ManualResolver(client, source_name)
            case _:
                print(f'Source {source_name} is not in possible sources: {__possible_sources__}')
    for source in sources.values():
        source.build_cache()
    return sources

def validate(cluster, sources):
    ''' Validate a single cluster against multiple reference sources '''
    for source_name, source in sources.items():
        print(source)
        print(source.resolve(cluster))
