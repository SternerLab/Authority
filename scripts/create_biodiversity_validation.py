
from rich import print
from rich.pretty   import pprint
from rich.progress import track

from resolution.validation.orcid  import *
from resolution.validation.scrape import *
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    articles         = client.jstor_database.articles
    orcid_scraper    = OrcidScraper('orcid_credentials.json')
    scrape(client, orcid_scraper, 'orcid', query='djohnson')

# from functools import partial
# import functools
# import itertools
# import requests
# import pymongo
# import pandas as pd
# import json
#
# from .download_bhl import parse_bhl_article
#
# from resolution.database.client import get_client
#
#
# def run():
#     client = get_client('mongo_credentials.json', local=True)
#     jstor_database = client.jstor_database
#     articles = jstor_database.articles
#     n = articles.count_documents({})
#
#     bhl_database = client.bhl_database
#     bhl = bhl_database.bhl
#     bhl = client.validation.bhl
#
#     with open('bhl_credentials.json', 'r') as infile:
#         credentials = json.load(infile)
#     api_key = credentials['api_key']
#
#     names = pd.read_csv('data/names.csv')
#     names.sort_values(by='count', ascending=False, inplace=True)
#
#     best_resolutions = dict()
#
#     with client.start_session(causal_consistency=True) as session:
#         for key in names['key']:
#             query = {'authors.key' : key}
#             total = 0
#             for article in articles.find(query, no_cursor_timeout=True, session=session):
#                 insertions = list(parse_bhl_article(article, key=api_key))
#                 total += len(insertions)
#                 if len(insertions) > 0:
#                     break
#                     # bhl.insert_many(insertions)
#             if total > 1:
#                 best_resolutions[key] = total
#             print(f'Resolved {total} articles for key {key}')
#
#             print(best_resolutions)

# BHL update script, shouldn't be needed!

# def run():
#     client = get_client('mongo_credentials.json', local=True)
#
#     jstor_database = client.jstor_database
#     articles = jstor_database.articles
#     articles.create_index('title')
#     articles.create_index('authors.key')
#
#     bhl = client.validation.bhl
#     n = bhl.count_documents({})
#
#     print(f'Found {n} BHL clusters')
#     for doc in track(bhl.find(), total=n):
#         ids = set()
#         key = doc['author']['key']
#
#         # Resolve by matching title, then author
#         for title in doc['titles']:
#             # pprint(title)
#             jstor_article = articles.find_one({'title' : title})
#             if (jstor_article is not None and
#                 key in {a['key'] for a in jstor_article['authors']}):
#                 ids.add(jstor_article['_id'])
#         # Resolve by author key
#         for jstor_article in articles.find({'authors.key' : key}):
#             if jstor_article is not None and jstor_article['title'] in doc['titles']:
#                 ids.add(jstor_article['_id'])
#
#         if ids:
#             # pprint({'_id' : doc['_id'], '$push' : {'mongo_ids' : list(ids)}})
#
#             bhl.update_one({'_id' : doc['_id']},
#                            {'$set' : {'mongo_ids' : [str(i) for i in ids]}},
#                            True)

# BHL Clean script, shouldn't be needed!

# def run():
#     client = get_client('mongo_credentials.json', local=True)
#
#     bhl = client.validation.bhl
#     n = bhl.count_documents({})
#
#     # Create a pipeline to identify the duplicates
#     pipeline = [
#         {"$group": {"_id": "$author_id", "count": {"$sum": 1}}},
#         {"$match": {"count": {"$gt": 1}}}
#     ]
#
#     # Execute the pipeline to find the duplicates
#     duplicates = list(bhl.aggregate(pipeline))
#
#     # Iterate through the duplicates and remove them
#     for duplicate in track(duplicates, total=len(duplicates), description='Removing BHL duplicates'):
#         author_id = duplicate["_id"]
#         bhl.delete_many({"author_id": author_id})
#
#     bhl.create_index('author_id', unique=True)
#
#     print(f'Found {n} BHL clusters')
#     for doc in track(bhl.find(), total=n):
#         key = doc['author']['key']
#         unique = []
#         seen = set()
#         ids = doc.get('mongo_ids', [])
#         for cluster in ids:
#             key = '-'.join(sorted(map(str, cluster)))
#             if key not in seen:
#                 unique.append([str(i) for i in cluster])
#                 seen.add(key)
#         bhl.update_one({'_id' : doc['_id']},
#                        {'$set' : {'mongo_ids' : unique}}, True)
