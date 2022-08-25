from pymongo import MongoClient
from rich.pretty import pprint
import rich.prompt

def run():
    print('Removing all databases and collections from MongoDB', flush=True)
    if rich.prompt.Confirm.ask('Are you absolutely sure you want to continue?'):
        client = MongoClient('localhost', 27017)
        for database_name in client.list_database_names():
            if database_name not in { 'admin'}:
                client.drop_database(database_name)

