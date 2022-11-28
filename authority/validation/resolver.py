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

    def resolve(self, cluster):
        gid = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'
        print(f'Resolving {key} for {self.name} ')

        article_ids = set(cluster['cluster_labels'].keys())
        resolved = {aid : (i, False) for i, aid in enumerate(article_ids)}

        # Merge clusters based on resolutions
        for cite in self.cache[key]:
            aid, cid = cite['article_id'], cite['citation_id']
            if aid in article_ids and cid is not None and cid in article_ids:
                merge(aid, cid, resolved)

        # # Filter unmerged clusters and decrement cluster labels appropriately
        return make_contiguous({k : v for k, (v, m) in resolved.items() if m})

    def yield_clusters(self, entry, articles):
        raise NotImplementedError

    def create(self, client, blocks, articles, query={}, skip=0):
        ''' Extract clusters based on self-citations '''
        total = blocks.count_documents(query)
        with client.start_session(causal_consistency=True) as session:
            for block in track(blocks.find(query, no_cursor_timeout=True,
                                           session=session).skip(skip),
                               total=total,
                               description=f'Building self-citations'):
                for entry in block['group']:
                    yield from self.yield_clusters(entry, articles)

    def build_cache(self):
        self.cache = defaultdict(list)
        total = self.collection.count_documents({})
        for cluster in track(self.collection.find({}), total=total,
                             description=f'Building {self.name} cache'):
            key = cluster['author']['key']
            self.cache[key].append(cluster)
