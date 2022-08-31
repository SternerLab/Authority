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
    reference_sets_pairs = client.reference_sets_pairs

    for ref_key in reference_sets_pairs.list_collection_names():
        print(ref_key)
        for pair in reference_sets_pairs[ref_key].find():
            pprint(pair)
            a, b = pair['pair']
            doc_a = articles.find_one({'_id' : a['ids']})
            doc_b = articles.find_one({'_id' : b['ids']})
            doc_a.update(**a['authors'])
            doc_b.update(**b['authors'])
            pprint(compare(doc_a, doc_b))
            break
