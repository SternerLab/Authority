from .mesh import parse_mesh_output
from pathlib import Path
import json
import requests
import itertools
import functools


from bson.objectid import ObjectId
from rich.pretty   import pprint
from rich.progress import Progress
from rich import print

from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock

from resolution.database.client import get_client

progress_lock = Lock()
count = 0

def insert_mesh_output(articles, mesh_output, progress, task):
    global count
    for article_id, words in mesh_output.items():
        try:
            result = articles.update_one(
                {'front.article-meta.article-id.#text' : article_id},
                {'$set' : {'mesh' : list(words)}})
            print(result)
            with progress_lock:
                progress.update(task, advance=1)
                count += 1
                print(count, flush=True)
        except TypeError as e:
            raise
            print(e, end='\n\n')

def insert_mesh(filename, articles=None, progress=None, task=None):
    mesh_output = parse_mesh_output(filename.read_text())
    insert_mesh_output(articles, mesh_output, progress, task)

def run():
    threads = 4

    get_client('mongo_credentials.json', local=False)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    upper_bound = articles.count_documents({})

    with Progress() as progress:
        task = progress.add_task('Inserting mesh articles', total=upper_bound)
        f = functools.partial(insert_mesh, articles=articles,
                              progress=progress, task=task)
        mesh_txt_files = Path('mesh_pre_fetched_txt/')
        with Pool(max_workers=threads) as pool:
            counts = pool.map(f, mesh_txt_files.glob('*.txt'))
