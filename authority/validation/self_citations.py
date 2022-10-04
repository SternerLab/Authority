from rich.pretty   import pprint
from rich.progress import track
from collections import defaultdict

from authority.parse.parse import process_citations, reorder_name

def self_citations(blocks, articles):
    ''' Extract clusters based on self-citations '''
    total    = blocks.count_documents({})
    length   = 0
    failures = 0
    for block in track(blocks.find(), total=total):
        self_cites = defaultdict(set)
        for entry in block['group']:
            last      = entry['authors']['last']
            article   = articles.find_one({'_id' : entry['ids']})
            # if 'citations' in article:
            #     citations = article['citations']
            # else:
            citations, new_failures, new_length = process_citations(article)
            failures += new_failures
            length   += new_length
            # if citations:
            #     pprint(citations)
            if length > 0 and new_failures > 0:
                print(f'Running: {failures/length:4.4f}% from {failures:4}/{length:4} failures ({new_failures:3}/{new_length:3} new)')

            for citation in citations:
                for author in citation['authors']:
                    if author['last'] == last:
                        self_cites[citation['title']].add(
                            (entry['title'], entry['authors']['last'], str(entry['ids'])))
                        break
        if len(self_cites) > 0:
            yield {k : list(v) for k, v in self_cites.items()}
