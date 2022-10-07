from rich.pretty   import pprint
from rich.progress import track
from rich import print
from collections import defaultdict

from authority.parse.parse import parse_citations, reorder_name

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
