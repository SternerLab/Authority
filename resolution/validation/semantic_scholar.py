from rich.pretty import pprint
import requests
import json

from ..parse.parse import parse_name, construct_name, remove_stop_words

from .resolver import Resolver
from .scrape import *

class SemanticScholarResolver(ScrapedResolver): # Use defaults
    pass

class SemanticScholarScraper(Scraper):
    def __init__(self, max_threads=2, max_rate=20, buffer=1):
        self.search_url = 'https://api.semanticscholar.org/graph/v1/paper/search?query='
        self.fill_url = 'https://api.semanticscholar.org/graph/v1/paper/batch?'
        self.fields = '?fields=title,authors,abstract,journal'

        self.max_threads = 2
        self.max_rate = max_rate
        self.thread_max_rate = max_rate / max_threads
        self.buffer = buffer
        self.name = 'semantic_scholar'

    def yield_works(self, title):
        yield title, None

    def yield_search(self, query, key='', desc='', max_rate=4.0):
        search_url = self.search_url + '+'.join(query.split(' ')) + self.fields
        response = requests.get(search_url).json()
        # Just go over the top ten responses given
        if 'data' not in response:
            pprint(response)
        else:
            id_json = dict(ids=[hit['paperId'] for hit in response['data']])
            full = requests.post(self.fill_url + self.fields, json=id_json).json()

            for hit in full['data']:
                if 'authors' in hit:
                    for author in hit['authors']:
                        print(author)
                    1/0
                    paper_id = hit['paperId']
                    title = remove_stop_words(hit['title'])
                    print(paper_id)
                    print(title)
                    yield paper_id, title, 1

