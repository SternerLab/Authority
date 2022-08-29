from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools

from authority.algorithm.compare import compare

def run():
    ''' Calculate the features for the different sets in the database '''
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets = client.reference_sets

    match_coll = 'first_initial:middle_initial:last:suffix'
    matches = reference_sets[match_coll]
    for group in matches.find():
        a, b, *rest = group['ids']
        auth_a, auth_b, *rest = group['authors']
        doc_a = articles.find_one({'_id' : a})
        doc_b = articles.find_one({'_id' : b})
        doc_a.update(**auth_a)
        doc_b.update(**auth_b)

        pprint(compare(doc_a, doc_b))

        break
        1/0

    1/0
