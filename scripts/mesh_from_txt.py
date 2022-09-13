from .mesh import parse_mesh_output
from pathlib import Path
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from rich.pretty import pprint
from rich import print

def insert_mesh_output(articles, mesh_output):
    for article_id, words in mesh_output.items():
        try:
            print('Updating', article_id)
            pprint(words)
            articles.update_one(
                {'front' : {'article-meta' : {'article-id' : {'#text' : article_id}}}},
                {'$set' : {'mesh' : list(words)}})
            print('Succeeded!', flush=True)
        except Exception as e:
            print(e)

def run():
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    mesh_txt_files = Path('mesh_pre_fetched_txt/')
    for filename in mesh_txt_files.glob('*.txt'):
        mesh_output = parse_mesh_output(filename.read_text())
        # insert lookup step mapping journal id to jstor id
        pprint(mesh_output)
        insert_mesh_output(articles, mesh_output)

# Journal ID lookup
#         {
# │   '_id': ObjectId('631ff6c3aeed79501565dd5e'),
# │   '@dtd-version': '1.0',
# │   '@article-type': 'research-article',
# │   'front': {
# │   │   'journal-meta': {
# │   │   │   'journal-id': [
# │   │   │   │   {
# │   │   │   │   │   '@xmlns:xlink': 'http://www.w3.org/1999/xlink',
# │   │   │   │   │   '@journal-id-type': 'jstor',
# │   │   │   │   │   '#text': 'orniscan'

# Article ID lookup
# │   │   'article-meta': {
# │   │   │   'article-id': {
# │   │   │   │   '@xmlns:xlink': 'http://www.w3.org/1999/xlink',
# │   │   │   │   '@pub-id-type': 'doi',
# │   │   │   │   '#text': '10.2307/3676580'
