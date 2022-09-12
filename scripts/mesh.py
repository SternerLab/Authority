import skr_web_api
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from rich.pretty import pprint
from rich import print
from itertools import islice

from authority.process.process import remove_stop_words
import unicodedata

def run():
    with open('umls_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
    sub.init_generic_batch('MTI', '')

    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    for article in articles.find(): # TODO add a check to see if mesh info is already present, then skip if it is
        abstract = article['abstract'].replace('\n', '')
        abstract = unicodedata.normalize('NFKD', abstract).encode('ascii', 'ignore').decode('ascii', 'ignore') # fun
        mongo_id = article["_id"]
        sub.set_batch_file('USERINPUT', f'{abstract}.')
        print(f'Submitting article to SKR API!', flush=True)
        response = sub.submit()
        assert response.status_code == 200, f'Bad response, {response}'
        print(f'Received {response.status_code}!', flush=True)

        mesh_output = []
        lines = response.content.decode('utf-8', errors='replace').split('\n')
        print('all lines:')
        pprint(lines)
        for i, line in enumerate(lines):
            print(i, line)
            if len(line.strip()) == 0 or '|' not in line:
                continue
            id_cell, *cells = line.split('|')
            mesh_output.extend(remove_stop_words(cells, 'mesh'))
        print('Updating', mongo_id)
        pprint(mesh_output)
        articles.update_one({'_id' : ObjectId(mongo_id)}, {'$set' : {'mesh' : list(set(mesh_output))}})
        print('Update finished!', flush=True)
