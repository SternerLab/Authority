from pymongo import MongoClient
from rich.pretty import pprint
import requests
import json


author_search_url = 'https://www.biodiversitylibrary.org/api3?op=AuthorSearch&authorname={author}&apikey={key}&format=json'
metadata_url = 'https://www.biodiversitylibrary.org/api3?op=GetAuthorMetadata&id={idn}&pubs=t&apikey={key}&format=json'

def run():
    print('Checking articles in MongoDB', flush=True)
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    collect = jstor_database.articles

    bhl_database = client.bhl_database
    bhl = bhl_database.bhl

    with open('bhl_credentials.json', 'r') as infile:
        credentials = json.load(infile)
    api_key = credentials['api_key']

    for article in collect.find():
        print(article['title'])
        for author in article['authors']:
            print('    ', author['full'])
            url = author_search_url.format(key=api_key, author=author['full'])
            response = requests.get(url).json()
            if response['Status'] == 'ok':
                for bhl_author in response['Result']:
                    pprint(bhl_author)
                    author_id = bhl_author['AuthorID']
                    metadata = requests.get(
                        metadata_url.format(key=api_key, idn=author_id)).json()
                    if metadata['Status'] == 'ok':
                        pprint(metadata['Result'])
        print()

    # pprint(article['authors'])
    # pprint(article['title'])
    # pprint(article['journal'])
    # pprint(article)
    # print(f'Counted {count} articles!', flush=True)
