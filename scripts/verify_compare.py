
from rich.pretty import pprint
from bson.son import SON
import itertools
from collections import defaultdict

from .features import compare_pair
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    pairs          = client.reference_sets_pairs

    for ref_key in pairs.list_collection_names():
        for pair in pairs[ref_key].find():
            pprint(compare_pair(pair, articles))
            1/0
