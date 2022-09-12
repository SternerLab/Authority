import skr_web_api
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from rich.pretty import pprint
from rich import print
from itertools import islice

from authority.process.process import remove_stop_words
import unicodedata

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
    # sub.init_generic_batch('MTI', '-default_MTI -opt1_DCMS -E --singleLineInput -display_simple3')
    sub.init_generic_batch('MTI', '-opt1L_DCMS -E') # The default options

    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    article_cursor = articles.find()
    batch_size = 4
    while True:
        batch = islice(article_cursor, batch_size)
        abstracts = []
        for article in batch:
            abstract = fix_unicode(article['abstract'])
            title    = fix_unicode(article['title'])
            mongo_id = article["_id"]
            abstracts.append(
                (mesh_format.format(article_id=mongo_id, title=title, abstract=abstract),
                 mongo_id))
        sub.set_batch_file('USERINPUT', '.\n\n'.join(a for a, _ in abstracts))
        pprint(sub.files)
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
        1/0
        articles.update_one({'_id' : ObjectId(mongo_id)}, {'$set' : {'mesh' : list(set(mesh_output))}})
        print('Update finished!', flush=True)
