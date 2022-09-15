import skr_web_api
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from rich.pretty import pprint
from rich import print
from itertools import islice

from authority.process.process import remove_stop_words
import unicodedata
from collections import defaultdict

mesh_format = '''UI  - {article_id}
TI  - {title}
AB  - {abstract}'''

def fix_unicode(s):
    s = s.replace('\n', '')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii', 'ignore')
    return s

def get_batch(article_cursor, batch_size):
    abstracts = []
    while len(abstracts) < batch_size:
        try:
            article = next(article_cursor)
            if len(article['abstract']) > 0:
                abstracts.append(
                    (mesh_format.format(
                        article_id=article["_id"],
                        title=fix_unicode(article['title']),
                        abstract=fix_unicode(article['abstract'])),
                     article['_id']))
        except StopIteration:
            break
    return abstracts

def parse_mesh_output(content):
    mesh_output = defaultdict(set)
    try:
        lines = content.decode('utf-8', errors='replace').split('\n')
    except AttributeError:
        lines = content.split('\n')
    for i, line in enumerate(lines):
        if len(line.strip()) == 0 or '|' not in line:
            continue
        id_cell, *cells = line.split('|')
        mesh_output[id_cell].update(remove_stop_words(cells, 'mesh'))
    return mesh_output

def insert_mesh_output(articles, mesh_output):
    for mongo_id, words in mesh_output.items():
        print('Updating', mongo_id)
        pprint(words)
        articles.update_one(
            {'_id' : ObjectId(mongo_id)},
            {'$set' : {'mesh' : list(words)}})


# See https://github.com/lhncbc/skr_web_python_api/blob/main/examples/generic_batch.py
with open('umls_credentials.json', 'r') as infile:
    credentials = json.load(infile)

def fetch_mesh(batch):
    print('Initializing SKR API', flush=True)
    sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
    # See https://lhncbc.nlm.nih.gov/ii/tools/MTI/help_info.html
    sub.init_generic_batch('MTI', '--priority 0 -opt1L_DCMS -E')
    print('Setting batch file', flush=True)
    sub.set_batch_file('USERINPUT', '.\n\n'.join(a for a, _ in batch))
    print(f'Submitting article to SKR API!', flush=True)
    response = sub.submit()
    assert response.status_code == 200, f'Bad response, {response}'
    print(f'Received {response.status_code}!', flush=True)
    return parse_mesh_output(response.content)

def run():
    distribute     = 1
    batch_size     = 2048

    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    article_cursor = articles.find(batch_size=batch_size)

    while True:
        print('Creating batches', flush=True)
        batch = get_batch(article_cursor, batch_size)
        if len(batch) == 0:
            break
        print('Distributing...', flush=True)
        mesh_output = fetch_mesh(batch)
        insert_mesh_output(articles, mesh_output)
        print('Update finished!', flush=True)
    print('Finished all batches!', flush=True)
