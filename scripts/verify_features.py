from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track


def run():
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database

    features         = client.features
    feature_groups_i = client.feature_groups_i
    feature_groups_a = client.feature_groups_a

    for ref_key in features.list_collection_names():
        print(ref_key)
        print('f', features[ref_key].count_documents({}))
        print('xa', feature_groups_a[ref_key].count_documents({}))
        # for doc in feature_groups_a[ref_key].find():
        #     pprint(doc)

    for ref_key in feature_groups_i.list_collection_names():
        print(ref_key)
        print('xi', feature_groups_i[ref_key].count_documents({}))
        # for doc in feature_groups_i[ref_key].find():
        #     pprint(doc)

