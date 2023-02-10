
from rich.pretty import pprint
from bson.son import SON
import itertools

from resolution.authority.compare import compare
from resolution.database.client import get_client

def run():
    ''' Verify that all subsets are created correctly '''

    client = get_client('mongo_credentials.json', local=True)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets_pairs = client.reference_sets_pairs
    lookup               = client.reference_sets_group_lookup

    ref_key = 'non_match'
    for pair in reference_sets_pairs[ref_key].find():
        pprint(pair)
        a, b = pair['pair']
        doc_a = articles.find_one({'_id' : a['ids']})
        doc_b = articles.find_one({'_id' : b['ids']})
        doc_a.update(**a['authors'])
        doc_b.update(**b['authors'])
        pprint(compare(doc_a, doc_b))
