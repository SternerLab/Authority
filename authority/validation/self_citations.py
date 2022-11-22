from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

import itertools

from authority.parse.parse import parse_citations

def merge(aid, cid, resolved):
    ''' Somewhat ugly because it accounts for edge cases.. '''
    # M is a boolean denoting if an entry has been merged already
    (prev, m), (prev_c, m_c) = resolved[aid], resolved[cid]
    u, v = min(prev, prev_c), max(prev, prev_c)
    for k, (l, m_k) in resolved.items():
        if l == v:
            resolved[k] = (u, True)
        elif l > v:
            resolved[k] = (resolved[k][0] - 1, m_k)

def make_contiguous(cluster):
    if not cluster:
        return cluster
    l = max(cluster.values()) + 1
    not_dropped = set(cluster.values())
    dropped = [c for c in range(l) if c not in not_dropped]
    update_label = lambda v : v - sum(1 for d in dropped if d < v)
    contiguous = {k : update_label(v) for k, v in cluster.items()}
    return contiguous

def build_self_citation_cache(self_citations):
    cache = defaultdict(list)
    total = self_citations.count_documents({})
    for cluster in track(self_citations.find({}), total=total, description='Building self-citation cache'):
        key = cluster['author']['key']
        cache[key].append(cluster)
    return cache

def resolve(cluster, self_citation_cache):
    gid = cluster['group_id']
    name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
    key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'
    print(f'Resolving {key} for self-citations..')

    article_ids = set(cluster['cluster_labels'].keys())
    resolved = {aid : (i, False) for i, aid in enumerate(article_ids)}

    # Merge clusters based on self-citation resolutions
    for cite in self_citation_cache[key]:
        aid, cid = cite['article_id'], cite['citation_id']
        if aid in article_ids and cid is not None and cid in article_ids:
            merge(aid, cid, resolved)

    # # Filter unmerged clusters and decrement cluster labels appropriately
    return make_contiguous({k : v for k, (v, m) in resolved.items() if m})

def batched(generator, batch_size=32):
    while True:
        batch = list(itertools.islice(generator, batch_size))
        if not batch:
            break
        else:
            yield batch

def self_citations(client, blocks, articles, query={}):
    ''' Extract clusters based on self-citations '''
    total    = blocks.count_documents(query)
    length   = 0
    failures = 0
    with client.start_session(causal_consistency=True) as session:
        for block in track(blocks.find(query, no_cursor_timeout=True,
                                       session=session),
                           total=total,
                           description='Building self-citations'):
            for entry in block['group']:
                source_author = entry['authors']
                article   = articles.find_one({'_id' : entry['ids']},
                                              no_cursor_timeout=True,
                                              session=session)
                citations, new_failures, new_length = parse_citations(article)
                failures += new_failures
                length   += new_length
                if length > 0 and new_failures > 0:
                    print(f'Running: {100*failures/length:4.4f}% from {failures:4}/{length:4} failures ({new_failures:3}/{new_length:3} new)')

                for citation in citations:
                    for cite_author in citation['authors']:
                        if (cite_author['last'] == source_author['last'] and
                            cite_author['first_initial'] == source_author['first_initial']):
                            cite_article = articles.find_one({'title' : citation['title']}, no_cursor_timeout=True, session=session)
                            print('resolved self-citation:', source_author, flush=True)
                            yield dict(
                                author=entry['authors'],
                                title=entry['title'],
                                article_id=str(article['_id']),
                                citation=citation,
                                citation_id=str(cite_article['_id']) if cite_article is not None else None)
