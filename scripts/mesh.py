import skr_web_api
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from rich.pretty import pprint
from rich import print
from itertools import islice

from authority.parse.parse import remove_stop_words
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
            if len(article['abstract']) > 0 and (
                'mesh' not in article or
                article['mesh'] == ''):
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
        id_cell = id_cell.split(':')[-1].strip()
        mesh_output[id_cell].update(remove_stop_words(cells, 'mesh'))
    return mesh_output

def insert_mesh_output(articles, mesh_output, session=None, use_obj_ids=True):
    for mongo_id, words in mesh_output.items():
        print('Updating', mongo_id)
        pprint(words)
        if use_obj_ids:
            query = {'_id' : ObjectId(mongo_id)},
        else:
            query = {'front.article-meta.article-id.#text' : doi}
        articles.update_one(query, {'$set' : {'mesh' : list(words)}}, session=session)

# See https://github.com/lhncbc/skr_web_python_api/blob/main/examples/generic_batch.py
with open('umls_credentials.json', 'r') as infile:
    credentials = json.load(infile)

def fetch_mesh(batch):
    print('Initializing SKR API', flush=True)
    sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
    # See https://lhncbc.nlm.nih.gov/ii/tools/MTI/help_info.html
    sub.init_generic_batch('MTI', '-opt1L_DCMS -E')
    print('Setting batch file', flush=True)
    sub.set_batch_file('USERINPUT', '.\n\n'.join(a for a, _ in batch))
    print(f'Submitting article to SKR API!', flush=True)
    response = sub.submit()
    assert response.status_code == 200, f'Bad response, {response}'
    print(f'Received {response.status_code}!', flush=True)
    return parse_mesh_output(response.content)

def run():
    batch_size     = 10240

    client = MongoClient('localhost', 27017)
    with client.start_session(causal_consistency=True) as session:
        jstor_database = client.jstor_database
        articles       = jstor_database.articles
        with articles.find(no_cursor_timeout=True, session=session) as article_cursor:
            while True:
                print('Creating batches', flush=True)
                batch = get_batch(article_cursor, batch_size)
                if len(batch) == 0:
                    break
                print('Distributing...', flush=True)
                mesh_output = fetch_mesh(batch)
                insert_mesh_output(articles, mesh_output, session=session)
                print('Update finished!', flush=True)
            print('Finished all batches!', flush=True)
