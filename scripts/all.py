from pymongo import MongoClient
from rich.pretty import pprint

from . import (
    parse,
    subset,
    sample_pairs,
    features,
    ratio_table,
    inference,
    validate
    )

def run():
    print('Running end-to-end resolution authority', flush=True)
    client = MongoClient('localhost', 27017)
    # Run the whole resolution authority in one go!
    # parse.run()
    subset.run()
    sample_pairs.run()
    features.run()
    ratio_table.run()
    inference.run()
    validate.run()
