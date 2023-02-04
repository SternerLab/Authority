
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.semantic_scholar import *
from resolution.validation.scrape import *
from resolution.database.client import get_client

def run():
    get_client('mongo_credentials.json', local=False)
    articles         = client.jstor_database.articles
    scraper          = SemanticScholarScraper()
    scrape(client, scraper, 'semantic_scholar')
