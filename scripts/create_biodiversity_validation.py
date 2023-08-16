
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.biodiversity import *
from resolution.validation.builder import *
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    articles             = client.jstor_database.articles
    # biodiversity_title_builder = BiodiversityTitleBuilder('bhl_credentials.json')
    # biodiversity_title_builder.build(client, query_authors=False, query_titles=True)
    biodiversity_builder = BiodiversityBuilder('bhl_credentials.json')
    biodiversity_builder.build(client, query_authors=True, query_titles=False)
