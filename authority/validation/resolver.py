from collections import defaultdict
from rich.progress import track
from .utils import *

class Resolver:
    ''' A base class for resolving labels for author clusters
        To be specifically used by google scholar, biodiversity, self citations'''
    def __init__(self, client, name):
        self.name  = name
        self.cache = None
        self.collection = client.validation[name]

    def yield_clusters(self, entry, articles):
        raise NotImplementedError

    def resolve(self, cluster):
        gid = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'

        if self.cache is not None:
            cursor = self.cache[key]
        else:
            print(f'{self.name} is NOT using cache')
            cursor = self.collection.find({'author.key' : key})

        reference_clusters = []
        resolved = 0
        for doc in cursor:
            reference_clusters.append(self.extract_cluster(doc))
            resolved += 1
        # if resolved > 0:
        #     print(reference_clusters)
        return reference_clusters

    def extract_cluster(self, doc):
        ''' Needs to account for scholar-type and bhl-type clusters'''
        clusters = doc.get('mongo_ids', [[]])
        if isinstance(clusters[0], list):
            return [str(_id) for cluster in clusters for _id in cluster]
        else:
            return [str(_id) for _id in clusters if _id is not None]

    def create(self, client, query={}, skip=0):
        ''' Extract clusters based on self-citations '''
        with client.start_session(causal_consistency=True) as session:
            blocks = client.reference_sets['first_initial_last_name']
            jstor_database = client.jstor_database
            articles       = jstor_database.articles
            total = blocks.count_documents(query)
            for block in track(blocks.find(query, no_cursor_timeout=True,
                                           session=session).skip(skip),
                               total=total,
                               description=f'Building {self.name}'):
                for entry in block['group']:
                    yield from self.yield_clusters(entry, articles)

    def build_cache(self):
        self.cache = defaultdict(list)
        total = self.collection.count_documents({})
        for cluster in track(self.collection.find({}), total=total,
                             description=f'Building {self.name} cache'):
            key = cluster['author']['key']
            # print(cluster)
            self.cache[key].append(cluster)
