from pymongo import MongoClient
from rich.pretty import pprint

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    jstor_database = client.jstor_database
    incomplete     = jstor_database.incomplete
    articles       = jstor_database.articles

    correct   = articles.count_documents({})
    incorrect = incomplete.count_documents({})
    print(f'Parsing created {correct} correct articles and left {incorrect} incomplete articles separated ({correct / (correct + incorrect):.4%})')

