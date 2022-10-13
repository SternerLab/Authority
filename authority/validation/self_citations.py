from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

from authority.parse.parse import parse_citations, reorder_name

def merge(aid, cid, resolved, i):
    ''' Somewhat ugly because it accounts for edge cases.. '''
    prev, prev_c = resolved[aid], resolved[cid]
    if prev is None and prev_c is not None:
        resolved[aid] = prev_c
    elif prev is not None and prev_c is None:
        resolved[cid] = prev
    elif prev is None and prev_c is None:
        resolved[aid] = i
        resolved[cid] = i
        i += 1
    elif prev is not None and prev_c is not None:
        u, v = min(prev, prev_c), max(prev, prev_c)
        for k, l in resolved.items():
            if l == v:
                resolved[k] = u
            elif l > v:
                resolved[k] -= 1
    return i

def resolve(cluster, self_citations):
    gid = cluster['group_id']
    name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
    key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'
    print(name, key)

    article_ids = set(cluster['cluster_labels'].keys())
    resolved = {aid : None for aid in article_ids}
    print(resolved)

    i = 0
    for cite in self_citations.find({'author.key' : key}):
        aid, cid = cite['article_id'], cite['citation_id']
        if aid in article_ids and cid is not None:
            print(aid, cid)
            i = merge(aid, cid, resolved, i)
    return {k : v for k, v in resolved.items() if v is not None}

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
                        cite_article = articles.find_one(
                                           {'title' : citation['title']})
                        print('resolved self-citation:', entry['authors'])
                        yield dict(
                            author=entry['authors'],
                            title=entry['title'],
                            article_id=str(article['_id']),
                            citation=citation,
                            citation_id=str(cite_article['_id']) if cite_article is not None else None)
                        break
