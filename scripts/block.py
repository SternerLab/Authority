from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def run():
    ''' Description of reference sets from Manuha's code, the paper, and my understanding:
    Manuha:
        matches: first name, last name, middle name, and suffix, total equality?
        non-matches: last name not equal

        firstname_match: first initial and last name equal
        firstname_non_match: last name does not match

        name_mixed_set: first initial equal, last name equal,

    Paper:
        matches: last name, first and middle initial, and suffix equal
        non-matches: last name and pubmed id not equal

        'names' meaning full names?
        name_mixed_set: select 1,000 names, and do all pairwise comparisons within this set
            name_attribute_match_set: extract article pairs with co-authors in common,
                two or more affiliation words, or two or more mesh terms in common
            name_attr_nonmatch_set: pairs with nothing but first author name in common

    Mine:
        blocks: last name and first initial are equal
        matches: first name, middle initial, and suffix are also equal
        non-matches: rejection sample from larger database, last name not equal

    We could succinctly reference these using the following convention:
        FI = First Initial
        FN = First Name
        LN = Last Name
        LI = Last Name
        MI = Middle Initial
        SX = Suffix

    Entailing:
        matches: FI-MI-LN-SX
        blocks:  FI-LN
        As well as all other combinations of these

    Keep in mind that the eventual goal is to fill out the r-table uniformly
    '''
    client = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles
    reference_sets = client.reference_sets
    blocks = reference_sets.blocks


    for by in (('last',), ('key',), ('first', 'last'), ('first_initial', 'last')):
        pipeline = [
            {'$unwind' : '$authors'},
            {'$group': {'_id': {k : f'$authors.{k}' for k in by}, 'count': {'$sum': 1}}},
            {'$sort': SON([('count', -1), ('_id', -1)])}
        ]
        result = articles.aggregate(pipeline)
        pprint(list(itertools.islice(result, 5)))

    pipeline = [
        {'$unwind' : '$authors'},
        {'$group': {'_id': {'language' : '$language'}, 'count': {'$sum': 1}}},
        {'$sort': SON([('count', -1), ('_id', -1)])}
    ]
    result = articles.aggregate(pipeline)
    pprint(list(itertools.islice(result, 20)))
    1/0
