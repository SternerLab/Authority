from pymongo import MongoClient
from rich.pretty import pprint
import xmltodict, json
import itertools

from authority.process.files import iter_xml_files

def run():
    print('Inserting articles into MongoDB', flush=True)
    zip_filename = 'xml_article_data/receipt-id-561931-jcodes-klmnop-part-002.zip'
    limit = 1000
    client = MongoClient('localhost', 27017)
    database = client.articles
    collect = database.main

    collect.drop() # Clear!

    for filename in itertools.islice(iter_xml_files(zip_filename), limit):
        with open(filename, 'r') as infile:
            collect.insert_one(xmltodict.parse(infile.read()))

    count = 0
    for article in collect.find():
        count += 1
        if count % 100 == 0:
            pprint(article)
    print(f'Inserted {count} articles!', flush=True)
