from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools

from authority.algorithm.compare import compare

def run():
    ''' Verify that all subsets are created correctly '''

    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets = client.reference_sets

    # match_coll = 'first_initial:middle_initial:last:suffix'
    set_key = 'non_match'
    matches = reference_sets[set_key]
    for group in matches.find():
        try:
            a, b, *rest = group['ids']
        except ValueError:
            continue
        auth_a, auth_b, *rest = group['authors']
        doc_a = articles.find_one({'_id' : a})
        doc_b = articles.find_one({'_id' : b})
        pprint(auth_a)
        pprint(auth_b)
        pprint(rest)
        pprint(doc_a['authors'])
        pprint(doc_b['authors'])
        doc_a.update(**auth_a)
        doc_b.update(**auth_b)

        print(doc_a['title'])
        print(doc_b['title'])
        pprint(compare(doc_a, doc_b))
        print()
        1/0

    1/0
