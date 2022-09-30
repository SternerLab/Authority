from rich.pretty   import pprint
from rich.progress import track
from collections import defaultdict

from authority.process.parse_citations import parse_citations, reorder_name

def self_citations(blocks, articles):
    ''' Extract clusters based on self-citations '''
    total = blocks.count_documents({})
    for block in track(blocks.find(), total=total):
        self_cites = defaultdict(set)
        for entry in block['group']:
            last      = entry['authors']['last']
            article   = articles.find_one({'_id' : entry['ids']})
            if 'citations' in article:
                citations = article['citations']
            else:
                citations = parse_citations(article)

            for citation in citations:
                for author in citation['authors']:
                    if author['last'] == last:
                        self_cites[citation['title']].add(
                            (entry['title'], entry['authors']['last'], str(entry['ids'])))
                        break
        if len(self_cites) > 0:
            yield {k : list(v) for k, v in self_cites.items()}
