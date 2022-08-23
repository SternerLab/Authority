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
    limit = 5
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    incomplete     = jstor_database.incomplete

    client.drop_database('blocks') # Clear!
    blocks = client.blocks

    # Hmmm, questionable
    incomplete.drop()
    articles.drop() # Clear!

    articles.create_index([('author.key', pymongo.ASCENDING)])

    incomplete_count = 0
    for filename in itertools.islice(iter_xml_files(zip_filename), limit):
        with open(filename, 'r') as infile:
            article = xmltodict.parse(infile.read())['article']
            try:
                processed = process(article)
                pprint(processed)
                inserted = articles.insert_one(processed)
                for author in processed['authors']:
                    blocks[author['key']].insert_one(
                            dict(mongo_id=inserted.inserted_id))
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
    print('Blocks by key:')
    for block_key in blocks.list_collection_names():
        matches = 0
        for i in blocks[block_key].find():
            matches += 1
        print(block_key, matches)

