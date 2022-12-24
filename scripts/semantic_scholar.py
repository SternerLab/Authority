from pymongo import MongoClient
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.semantic_scholar import *
from resolution.validation.scrape import *

def run():
    client           = MongoClient('localhost', 27017)
    articles         = client.jstor_database.articles
    scraper          = SemanticScholarScraper()
    scrape(client, scraper, 'semantic_scholar')
