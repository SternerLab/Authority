from pymongo import MongoClient
from rich.pretty   import pprint
from rich import print
import pickle

from bson.objectid import ObjectId

import seaborn as sns
import matplotlib.pyplot as plt

def run():
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    inferred       = client.inferred
    inferred_blocks = inferred['first_initial_last_name']
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

    query = {}
    # query = {'group_id' : {'first_initial' : 'a', 'last' : 'johnson'}}
    # # query = {'group_id' : {'first_initial' : 'r', 'last' : 'short'}}

    print('Validating..')
    print(inferred_blocks.find({}))

    for cluster in inferred_blocks.find(query):
        pprint(cluster['group_id'])
        pprint(cluster['cluster_labels'])
        pprint(cluster.keys())
        for prior_key in ('match_prior', 'prior'):
            prior = cluster['prior']
            print(f'{prior_key} : {prior:.4%}')
        # for prob_key in ('probs', 'original_probs', 'fixed_probs'):
        for prob_key in ('original_probs',):
            probs = pickle.loads(cluster[prob_key])
            fig = sns.heatmap(probs).get_figure()
            fig.savefig(f'plots/{prob_key}.png')
            if len(cluster['cluster_labels']) > 4:
                plt.show()

        found_clusters = 0
        for mongo_id, cluster_label in cluster['cluster_labels'].items():
            cite_cluster = self_citations.find_one({'_id' : ObjectId(mongo_id)})
            pprint(cite_cluster)
            if cite_cluster is not None:
                found_clusters += 1
            article = articles.find_one({'_id' : ObjectId(mongo_id)})
            print('mongo_id', mongo_id, 'cluster: ', cluster_label)
            print('citation cluster')
            pprint(cite_cluster)
            # pprint(article)
            print()
        print(cluster['group_id'], f'found {found_clusters} clusters')
