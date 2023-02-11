from rich.pretty import pprint
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from functools import partial

import logging
import itertools
import requests
import json
from time import time, sleep
from collections import defaultdict

log = logging.getLogger('rich')

from .resolver import Resolver
from .scrape import *
from ..parse.parse import parse_name, construct_name, remove_stop_words

author_search_url = 'https://www.biodiversitylibrary.org/api3?op=AuthorSearch&authorname={author}&apikey={key}&format=json'
metadata_url = 'https://www.biodiversitylibrary.org/api3?op=GetAuthorMetadata&id={idn}&pubs=t&apikey={key}&format=json'

class BiodiversityResolver(ScrapedResolver): # Use defaults
    pass

class BiodiversityScraper(Scraper):
    def __init__(self, creds_path, max_threads=8, max_rate=120., buffer=0.):
        with open(creds_path, 'r') as infile:
            credentials = json.load(infile) # save :)
            self.api_key = credentials['api_key']
        self.max_threads = max_threads
        self.max_rate = max_rate
        self.thread_max_rate = max_rate / max_threads
        self.buffer = buffer
        self.name = 'biodiversity'

    def yield_works(self, bhl_author):
        author_id = bhl_author['AuthorID']
        metadata = requests.get(metadata_url.format(key=key, idn=author_id)).json()
        if metadata['Status'] == 'ok':
            for result in metadata['Result']:
                try:
                    titles = [remove_stop_words(pub['Title'])
                              for pub in metadata['Publications']]
                    for title in titles:
                        yield title, ''
                except ValueError as e:
                    print(f'BHL Could not parse {result["Name"]}, resulting in {e}')

    def yield_search(self, query, key='', desc='', max_rate=4.0):
        del key, desc # These aren't relevant to BHL, key is a JSON key
        first, *rest = query
        author = f'{first.upper}. {" ".join(rest).title()}'

        # yield id, doc, n_requests
        n_requests = 1
        url = author_search_url.format(key=self.api_key, author=author)
        response = requests.get(url).json()
        if response['Status'] == 'ok':
            for bhl_author in response['Result']:
                author_id = bhl_author['AuthorID']
                n_requests += 1
                yield author_id, bhl_author, n_requests

# If we'd like to compare against BHL names
# def parse_bhl_name(bhl_name):
#     print(bhl_name)
#     last, first, *ex = bhl_name.split(',')
#     data = {'given-names' : first.strip(), 'surname' : last.strip()}
#     return parse_name(data, order=0)

''' Example JSON data
{
│   'AuthorID': '275745',
│   'Name': 'Snow, R.',
│   'CreatorUrl': 'https://www.biodiversitylibrary.org/creator/275745'
}
[
│   {
│   │   'AuthorID': '275745',
│   │   'Name': 'Snow, R.',
│   │   'CreatorUrl': 'https://www.biodiversitylibrary.org/creator/275745',
│   │   'CreationDate': '2021/08/22 08:00:40',
│   │   'Publications': [
│   │   │   {
│   │   │   │   'BHLType': 'Part',
│   │   │   │   'FoundIn': 'Metadata',
│   │   │   │   'Volume': '37',
│   │   │   │   'Authors': [{'Name': 'Snow, R.'}],
│   │   │   │   'PartUrl': 'https://www.biodiversitylibrary.org/part/319066',
│   │   │   │   'PartID': '319066',
│   │   │   │   'Genre': 'Article',
│   │   │   │   'Title': 'The conduction of geotropic excitation in roots',
│   │   │   │   'ContainerTitle': 'Annals of botany',
│   │   │   │   'Date': '1923-01',
│   │   │   │   'PageRange': '43--53'
│   │   │   }
│   │   ]
│   }
]

'''
