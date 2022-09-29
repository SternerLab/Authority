from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
import itertools
import pymongo
from pathlib import Path
import zipfile

def run():
    xml_dir = Path('xml_article_data/')
    jstor_pack = [zip_filename for zip_filename in xml_dir.glob('*.zip')
                  if 'JSTOR' in str(zip_filename)]
    for zip_filename in track(jstor_pack):
        with zipfile.ZipFile(zip_filename, 'r') as zfile:
            zfile.extractall(xml_dir)

