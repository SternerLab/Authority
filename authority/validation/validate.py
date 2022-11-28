from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle
import pandas as pd
import pymongo

from bson.objectid import ObjectId

from .metrics import *
from .self_citations import resolve, make_contiguous, build_self_citation_cache

def validate():
    pass
