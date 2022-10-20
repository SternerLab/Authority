from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

from authority.parse.parse import parse_citations, reorder_name

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
    print('dropped', dropped)
    update_label = lambda v : v - sum(1 for d in dropped if d < v)
    print('pre', cluster)
    contiguous = {k : update_label(v) for k, v in cluster.items()}
    print('post', contiguous)
    return contiguous

def resolve(cluster, self_citations):
    gid = cluster['group_id']
    name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
    key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'
    print(name, key)

    article_ids = set(cluster['cluster_labels'].keys())
    resolved = {aid : (i, False) for i, aid in enumerate(article_ids)}
    print(resolved)

    # Merge clusters based on self-citation resolutions
    for cite in self_citations.find({'author.key' : key}):
        aid, cid = cite['article_id'], cite['citation_id']
        if aid in article_ids and cid is not None and cid in article_ids:
            print(aid, cid)
            merge(aid, cid, resolved)

    # # Filter unmerged clusters and decrement cluster labels appropriately
    # dropped = []
    # for k, (v, m) in list(resolved.items()):
    #     if not m:
    #         dropped.append(v)
    return make_contiguous({k : v for k, (v, m) in resolved.items() if m})
    # print('dropped', dropped)
    # print('pre', resolved)
    # update_label = lambda v : v - sum(1 for d in dropped if d < v)
    # resolved = {k : update_label(v) for k, (v, m) in resolved.items()
    #             if m}
    # print('post', resolved)
    # return resolved


def self_citations(blocks, articles, query={}):
    ''' Extract clusters based on self-citations '''
    total    = blocks.count_documents(query)
    length   = 0
    failures = 0
    for block in track(blocks.find(query), total=total):
        for entry in block['group']:
            # print(entry)
            last      = entry['authors']['last']
            article   = articles.find_one({'_id' : entry['ids']})
            citations, new_failures, new_length = parse_citations(article)
            failures += new_failures
            length   += new_length
            if length > 0 and new_failures > 0:
                print(f'Running: {100*failures/length:4.4f}% from {failures:4}/{length:4} failures ({new_failures:3}/{new_length:3} new)')

            # print(citations)
            for citation in citations:
                # print(citation)
                for author in citation['authors']:
                    # print(author['last'], last)
                    if author['last'] == last:
                        cite_article = articles.find_one({'title' : citation['title']})
                        print('resolved self-citation:', entry['authors'])
                        yield dict(
                            author=entry['authors'],
                            title=entry['title'],
                            article_id=str(article['_id']),
                            citation=citation,
                            citation_id=str(cite_article['_id']) if cite_article is not None else None)
                        break
