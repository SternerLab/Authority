
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.semantic_scholar import *
from resolution.validation.builder          import *
from resolution.database.client import get_client

def run():
    client   = get_client('mongo_credentials.json', local=True)
    articles = client.jstor_database.articles
    builder  = SemanticScholarBuilder()
    builder.build(client, query_titles=True)
