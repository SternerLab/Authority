from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track
import xmltodict, json
import itertools
import pymongo
from pathlib import Path

from authority.process.files import iter_xml_files
from authority.process.process import process, IncompleteEntry # hmm

def run():
    print('Inserting articles into MongoDB', flush=True)
    incomplete_count = 0
    xml_dir = Path('xml_article_data/')
    client = MongoClient('localhost', 27017)
    client.drop_database('jstor_database') # Be careful!
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    incomplete     = jstor_database.incomplete

    for zip_filename in xml_dir.glob('*.zip'):
        if 'JSTOR' in str(zip_filename):
            print(f'skipping {zip_filename},\n    which needs to be unzipped using ./run unzip first')
            continue
        print(f'parsing {zip_filename} into mongodb')

        articles.create_index([('author.key', pymongo.ASCENDING)])

        iterator = iter_xml_files(zip_filename)
        total = next(iterator) # first element is number of files in zip
        for filename in track(iterator, description='Parsing..', total=total):
            with open(filename, 'r') as infile:
                article = xmltodict.parse(infile.read())['article']
                try:
                    processed = process(article)
                    inserted = articles.insert_one(processed)
                except IncompleteEntry as e:
                    article['reason'] = str(e)
                    incomplete.insert_one(article)
                    incomplete_count += 1

    count = 0
    for article in articles.find():
        count += 1
    print(f'Inserted {count} articles!', flush=True)
    print(f'Skipped {incomplete_count} articles', flush=True)
    for article in incomplete.find():
        print(article['reason'])
