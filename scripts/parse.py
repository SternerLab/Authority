from pymongo import MongoClient
from rich.pretty import pprint
import xmltodict, json
import itertools

from authority.process.files import iter_xml_files
from authority.process.process import process, IncompleteEntry # hmm

def run():
    print('Inserting articles into MongoDB', flush=True)
    zip_filename = 'xml_article_data/receipt-id-561931-jcodes-klmnop-part-002.zip'
    limit = 10000
    client = MongoClient('localhost', 27017)
    database = client.articles
    collect = database.main

    collect.drop() # Clear!

    for filename in itertools.islice(iter_xml_files(zip_filename), limit):
        with open(filename, 'r') as infile:
            try:
                collect.insert_one(process(xmltodict.parse(infile.read())))
            except IncompleteEntry:
                pass # TODO count these to report in paper
    1/0

    count = 0
    for article in collect.find():
        count += 1
        pprint(article['article']['front']['article-meta']['contrib-group']['contrib'])
    print(f'Inserted {count} articles!', flush=True)
