from pymongo import MongoClient
from rich.pretty import pprint
import xmltodict, json
import itertools
import pymongo

from authority.process.files import iter_xml_files
from authority.process.process import process, IncompleteEntry # hmm

def run():
    print('Inserting articles into MongoDB', flush=True)
    zip_filename = 'xml_article_data/receipt-id-561931-jcodes-klmnop-part-002.zip'
    limit = 1000
    client = MongoClient('localhost', 27017)
    client.drop_database('jstor_database')
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    incomplete     = jstor_database.incomplete

    articles.create_index([('author.key', pymongo.ASCENDING)])

    incomplete_count = 0
    for filename in itertools.islice(iter_xml_files(zip_filename), limit):
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
    print(f'Skipped {incomplete} articles', flush=True)
    for article in incomplete.find():
        print(article['reason'])
