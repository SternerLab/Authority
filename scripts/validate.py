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

    # pprint(bhl.find_one())
    # pprint(scholar.find_one())
    # pprint(self_citations.find_one())

    query = {}
    name = 'aheimerl'
    name = 'ajohnson'
    name = 'rshot'
    name = 'budiadi'
    name = 'aelvebakk'
    first_initial, *last = name
    last = ''.join(last)
    # query = {'group_id' : {'first_initial' : first_initial, 'last' : last}}
    query = {}

    print('Validating..')
    print(inferred_blocks.find({}))

    for cluster in inferred_blocks.find(query):
        gid  = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        pprint(name)

        pprint(cluster['cluster_labels'])
        pprint(cluster.keys())
        for prior_key in ('match_prior', 'prior'):
            prior = cluster['prior']
            print(f'{prior_key} : {prior:.4%}')
        # for prob_key in ('probs', 'original_probs', 'fixed_probs'):
        # for prob_key in ('original_probs',):
        for prob_key in ('probs',):
            probs = pickle.loads(cluster[prob_key])
            plt.cla(); plt.clf(); plt.close(); # To avoid multiple cbars
            axes = sns.heatmap(probs, vmin=0., vmax=1.)
            axes.set_xlabel('Paper')
            axes.set_ylabel('Paper')
            axes.set_title(f'Pairwise probabilities for papers authored by {name}')
            fig  = axes.get_figure()

            fig.savefig(f'plots/probability_matrices/{name}_{prob_key}.png')
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
                print()
            else:
                print(f'{name} has no available self-citation clusters')
        if found_clusters > 0:
            print(name, f'found {found_clusters} clusters')
