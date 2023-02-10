
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.orcid  import *
from resolution.validation.scrape import *
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    articles         = client.jstor_database.articles
    orcid_scraper    = OrcidScraper('orcid_credentials.json')
    scrape(client, orcid_scraper, 'orcid', query='djohnson')
