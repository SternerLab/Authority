from pymongo import MongoClient
from rich.pretty import pprint
import xmltodict, json

filename = 'xml_article_data/micr/1955/1/1/i265301/1484407/1484407.xml'

def run():
    print('Inserting an XML article into MongoDB', flush=True)
    client = MongoClient('localhost', 27017)

    database = client.articles

    collect = database.main

    with open(filename, 'r') as infile:
        collect.insert_one(xmltodict.parse(infile.read()))

    pprint(collect.find_one())
