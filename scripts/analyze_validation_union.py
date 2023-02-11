
from rich.pretty   import pprint
from rich import print
import dill as pickle

from bson.objectid import ObjectId

import seaborn as sns
import matplotlib.pyplot as plt
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['block']
    inferred_blocks.create_index('group_id')

    articles = jstor_database.articles
    articles.create_index('title')
    articles.create_index('authors.key')

    val            = client.validation
    bhl            = val.bhl
    scholar        = val.google_scholar_doi
    self_citations = val.self_citations

    pprint(bhl.find_one())
    pprint(scholar.find_one())
    pprint(self_citations.find_one())

    total_found_clusters = 0
    for cluster in inferred_blocks.find():
        found_clusters = 0
        for mongo_id, cluster_label in cluster['cluster_labels'].items():
            cite_cluster = self_citations.find_one({'_id' : ObjectId(mongo_id)})
            if cite_cluster is not None:
                found_clusters += 1
            else:
                # print(f'id={mongo_id} not found in self-citations')
                pass
            total_found_clusters += found_clusters
        print(cluster['group_id'], f'found {found_clusters} clusters ({total_found_clusters} total)')

    total_article_clusters = 0
    for article in articles.find():
        cite_cluster = self_citations.find_one({'_id' : ObjectId(article['_id'])})
        if cite_cluster is not None:
            total_article_clusters += 1
    print(f'There are {total_article_clusters} valid clusters')

from rich.pretty import pprint
from rich import print
import pandas as pd

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    val        = client.validation
    val_types  = val.list_collection_names()
    print(val_types)
    1/0

    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)

    for tup in names.itertuples():
        print(f'Considering {tup.key}, count {tup.count}')
        missing = False
        total_overlap = 0
        for val_type in val_types:
            col = val[val_type]
            print('Sanity checking validation size', col.count_documents({}))
            overlap = 0
            for match in col.find({'author' : {'key' : tup.key}}):
                overlap += 1
            total_overlap += overlap
            if overlap == 0:
                print(f'No author with key {tup.key} in source {val_type}')
                missing = True
            else:
                print(f'Resolved key {tup.key} in source {val_type} with overlap {overlap}')
        if missing:
            print(f'{tup.key} missing from at least one validation source')
        else:
            print(f'{tup.key} is present in all validation sources, and has count {tup.count} with {total_overlap} total overlapping entries')
