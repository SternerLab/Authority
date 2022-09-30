from pymongo import MongoClient
from rich.pretty import pprint

def run():
    # db.command('cloneCollection', **{'collection': 'databaseName.source_collection',
    #            'from': "another_host:another_port"})

    client = MongoClient('localhost', 27017)
    client.validation.bhl.insert_many(client.bhl_database.bhl.find())
    client.drop_database('bhl_database')

