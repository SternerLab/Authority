
from rich.pretty import pprint
from resolution.database.client import get_client

def run():
    print('Checking articles in MongoDB', flush=True)
    client = get_client('mongo_credentials.json', local=True)

    jstor_database = client.jstor_database
    incomplete     = jstor_database.incomplete
    articles       = jstor_database.articles

    correct   = articles.count_documents({})
    incorrect = incomplete.count_documents({})
    print(f'Parsing created {correct} correct articles and left {incorrect} incomplete articles separated ({correct / (correct + incorrect):.4%})')

