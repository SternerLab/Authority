from pymongo import MongoClient
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.orcid  import *
from resolution.validation.scrape import *

def run():
    client           = MongoClient('localhost', 27017)
    articles         = client.jstor_database.articles
    orcid_scraper    = OrcidScraper('orcid_credentials.json')
    scrape(client, orcid_scraper, 'orcid', query='djohnson')
