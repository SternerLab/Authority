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

def run():
    with open('umls_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    # See https://github.com/lhncbc/skr_web_python_api/blob/main/examples/generic_batch.py
    sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
    # See https://lhncbc.nlm.nih.gov/ii/tools/MTI/help_info.html
    sub.init_generic_batch('MTI', '-opt1L_DCMS -E') # The default options used previously

    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    article_cursor = articles.find()
    batch_size = 128
    while True:
        batch = islice(article_cursor, batch_size)
        abstracts = []
        for article in batch:
            abstracts.append(
                (mesh_format.format(
                    article_id=article["_id"],
                    title=fix_unicode(article['title']),
                    abstract=fix_unicode(article['abstract'])),
                 article['_id']))
        if len(abstracts) == 0:
            break
        sub.set_batch_file('USERINPUT', '.\n\n'.join(a for a, _ in abstracts))
        print(f'Submitting article to SKR API!', flush=True)
        response = sub.submit()
        assert response.status_code == 200, f'Bad response, {response}'
        print(f'Received {response.status_code}!', flush=True)

        mesh_output = defaultdict(set)
        lines = response.content.decode('utf-8', errors='replace').split('\n')
        print('all lines:')
        pprint(lines)
        for i, line in enumerate(lines):
            if len(line.strip()) == 0 or '|' not in line:
                continue
            print(i, line)
            id_cell, *cells = line.split('|')
            mesh_output[id_cell].update(remove_stop_words(cells, 'mesh'))
        for mongo_id, words in mesh_output.items():
            print('Updating', mongo_id)
            pprint(words)
            articles.update_one(
                {'_id' : ObjectId(mongo_id)},
                {'$set' : {'mesh' : list(words)}})
        print('Update finished!', flush=True)
