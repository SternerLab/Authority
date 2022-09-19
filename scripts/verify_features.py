from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track


def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database

    features       = client.features
    feature_groups = client.feature_groups

    for ref_key in features.list_collection_names():
        print(ref_key)
        for group in feature_groups[ref_key].find():
            pprint(group)

