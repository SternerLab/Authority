
from pymongo.server_api import ServerApi
from pymongo import MongoClient

from urllib.parse import quote_plus
from rich.prompt import Prompt
from rich.pretty import pprint

from subprocess import call, check_output
import shlex

db_url    = 'authorresolution.yprf1.mongodb.net'
db_params = '/?retryWrites=true&w=majority'

from resolution.database.client import get_client

def run():
    raw_username  = Prompt.ask('Username')
    raw_password  = Prompt.ask('Password', password=True)
    username      = quote_plus(raw_username)
    password      = quote_plus(raw_password)
    mongo_url     = f'mongodb+srv://{username}:<{password}>@{db_url}'
    remote_client = MongoClient(f'{mongo_url}{db_params}', server_api=ServerApi('1'))
    for db_name in remote_client.list_database_names():
        print(db_name)
