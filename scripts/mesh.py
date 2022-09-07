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
    article_cursor = articles.find()
    batch_size     = 1024
    batch_size     = 8
    batch_size     = 2
    batch_size     = 16

    ''' Create a batch of 1024 abstracts in memory, submit them, and parse them into the database immediately '''
    while True:
        # First create a large string containing the batch of abstracts, and submit it to SKR
        batch = islice(article_cursor, batch_size)
        abstracts = []
        for article in batch:
            abstract = article['abstract'].replace('\n', '')
            abstract = unicodedata.normalize('NFKD', abstract).encode('ascii', 'ignore').decode('ascii', 'ignore') # fun
            abstracts.append(f'{article["_id"]}|{abstract}.') # period is important apparently!
        if len(abstracts) == 0:
            print(f'Finished adding all mesh terms!')
            break
        pprint(abstracts)
        sub.set_batch_file('USERINPUT', '\n'.join(abstracts))
        print(f'Submitting {batch_size} articles to SKR API!', flush=True)
        response = sub.submit()
        assert response.status_code == 200, f'Bad response, {response}'
        print(f'Received {response.status_code}!', flush=True)

        # Using the results
        mesh_output = None # Store lines of results for each abstract
        mongo_id    = None

        lines = response.content.decode('utf-8', errors='replace').split('\n')
        print('all lines:')
        pprint(lines)
        for i, line in enumerate(lines):
            print(i, line)
            if len(line.strip()) == 0 or '|' not in line:
                continue
            id_cell, *cells = line.split('|')
            if ' ' in id_cell or i == len(lines) - 3:
                # Since this cell has ended, enter the mesh terms into mongodb if it is not the first cell
                if mesh_output is not None and mongo_id is not None:
                    print('Updating', mongo_id)
                    pprint(mesh_output)
                    articles.update_one({'_id' : ObjectId(mongo_id)}, {'mesh' : list(set(mesh_output))})
                    print('Update finished!', flush=True)
                # Create the *next* mongo_id variable, overwriting the old one, reset mesh output variable
                if ' ' in id_cell:
                    _, mongo_id = id_cell.split(' ')
                    mesh_output = []
            mesh_output.extend(remove_stop_words(cells, 'mesh'))
        break


