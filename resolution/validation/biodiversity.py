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
from .builder import *
from ..parse.parse import parse_name, construct_name, remove_stop_words


class BiodiversityResolver(DefaultBuiltResolver): # Use defaults
    pass

class BiodiversityBuilder(Builder):
    def __init__(self, creds_path, max_threads=16, max_rate=240., buffer=0.):
        with open(creds_path, 'r') as infile:
            credentials = json.load(infile) # save :)
            self.api_key = credentials['api_key']
        self.author_search_url = 'https://www.biodiversitylibrary.org/api3?op=AuthorSearch&authorname={author}&apikey={key}&format=json'
        self.metadata_url = 'https://www.biodiversitylibrary.org/api3?op=GetAuthorMetadata&id={idn}&pubs=t&apikey={key}&format=json'
        self.publication_search_url= 'https://www.biodiversitylibrary.org/api3?op=PublicationSearch&searchterm={query}&apikey={key}&format=json'
        self.max_threads = max_threads
        self.max_rate = max_rate
        self.thread_max_rate = max_rate / max_threads
        self.buffer = buffer
        self.name = 'biodiversity'

    def yield_works(self, bhl_author):
        try:
            author_id = bhl_author['AuthorID']
            metadata = requests.get(self.metadata_url.format(key=self.api_key, idn=author_id)).json()
            if metadata['Status'] == 'ok':
                for result in metadata['Result']:
                    try:
                        titles = [remove_stop_words(pub['Title'])
                                  for pub in result['Publications']]
                        log.info(f'Titles: {titles}')
                        for title in titles:
                            yield title, ''
                    except (ValueError, KeyError) as e:
                        print(f'BHL Could not parse {result["Name"]}, resulting in {e}')
        except:
            pass

    def yield_search(self, query, key='', desc='', max_rate=4.0):
        del key, desc # These aren't relevant to BHL, key is a JSON key
        # yield id, doc, n_requests
        log.info(f'Biodiversity query: {query}')
        n_requests = 1
        url = self.author_search_url.format(key=self.api_key, author=query)
        response = requests.get(url).json()
        if response['Status'] == 'ok':
            log.info(f'Got normal response.. parsing')
            for bhl_author in response['Result']:
                log.info(f'Author: {bhl_author}')
                author_id = bhl_author['AuthorID']
                n_requests += 1
                yield author_id, bhl_author, n_requests
        else:
            log.info(f'Got {response["Status"]}')

class BiodiversityTitleBuilder(BiodiversityBuilder):
    def yield_works(self, publications):
        for pub in publications:
            title = remove_stop_words(pub['Title'])
            yield title, ''

    def yield_search(self, query, key='', desc='', max_rate=4.0):
        del key, desc # These aren't relevant to BHL, key is a JSON key
        log.info(f'Biodiversity query: {query}')
        n_requests = 1
        url = self.publication_search_url.format(key=self.api_key, query=query)
        response = requests.get(url).json()
        if response['Status'] == 'ok':
            log.info(f'Got normal response.. parsing')
            yield None, response['Result'], n_requests
        else:
            log.info(f'Got {response["Status"]}')

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
