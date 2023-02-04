
from rich.pretty import pprint
from bson.son import SON
import itertools
from resolution.database.client import get_client

def run():
    get_client('mongo_credentials.json', local=False)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets = client.reference_sets


    for ref_key in reference_sets.list_collection_names():
        print(ref_key, reference_sets[ref_key].count_documents({}))
