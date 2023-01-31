from pymongo import MongoClient
from pymongo.server_api import ServerApi

from urllib.parse import quote_plus
from rich.prompt import Prompt
from rich.pretty import pprint

from subprocess import call, check_output
import shlex

db_url    = 'authorresolution.yprf1.mongodb.net'
db_params = '/?retryWrites=true&w=majority'

def run():
    raw_username  = Prompt.ask('Username')
    raw_password  = Prompt.ask('Password', password=True)
    username      = quote_plus(raw_username)
    password      = quote_plus(raw_password)
    mongo_url     = f'mongodb+srv://{username}:<{password}>@{db_url}'
    remote_client = MongoClient(f'{mongo_url}{db_params}', server_api=ServerApi('1'))
    print('Successfully connected to remote MongoDB!')
    print(check_output('docker ps', shell=True))
    docker_id = Prompt.ask('Docker image:')
    local_client = MongoClient('localhost', 27017)
    for db_name in local_client.list_database_names():
        print(f'Transferring DB: {db_name}')
        pre = f'docker exec -i {docker_id}'
        local_dump = f'/workspace/mongodump_{db_name}'
        call(f'{pre} /usr/bin/mongodump --db {db_name} --out /{db_name}_dump', shell=True)
        call(f'docker cp {docker_id}:/{db_name}_dump {local_dump}', shell=True)
        print(check_output(f'{pre} /usr/bin/ls /', shell=True))
        call(f'{pre} /usr/bin/rm -rf /{db_name}_dump', shell=True)
        call(f'mongorestore --uri "mongodb+srv://authorresolution.yprf1.mongodb.net" --username {username} {local_dump}', shell=True)
