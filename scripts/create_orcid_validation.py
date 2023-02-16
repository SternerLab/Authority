
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.orcid  import *
from resolution.validation.builder import *
from resolution.database.client import get_client

def run():
    client        = get_client('mongo_credentials.json', local=True)
    articles      = client.jstor_database.articles
    orcid_builder = OrcidBuilder('orcid_credentials.json')
    orcid_builder.build(client, query_authors=True, query_titles=True)
