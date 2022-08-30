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
    client         = MongoClient('localhost', 27017)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    client.drop_database('reference_sets')
    reference_sets = client.reference_sets

    ''' Create matching based on different criteria '''
    criteria = [('first',),
                ('last',),
                ('first', 'last'),
                ('first_initial', 'last'),                             # candidates
                ('first_initial', 'middle_initial', 'last', 'suffix'), # matches
                ('full',)
                ]
    for fields in criteria:
        set_name = ':'.join(fields)
        pipeline = [
            {'$unwind' : '$authors'},
            {'$group': {
                '_id'    : {k : f'$authors.{k}' for k in fields},
                'count'  : {'$sum': 1},
                'titles' : {'$push' : '$title'},
                'ids'    : {'$push' : '$_id'},
                'authors': {'$push' : '$authors'}
                }},
            {'$sort': SON([('count', -1), ('_id', -1)])}
        ]
        result = articles.aggregate(pipeline)
        reference_sets[set_name].insert_many(result)
        result = articles.aggregate(pipeline)
        # pprint(list(itertools.islice(result, 5)))

    ''' Create non-matching set by sampling articles with different last names '''
    match_criteria = 'first_initial:middle_initial:last:suffix'
    n_pairs = reference_sets[match_criteria].count_documents({})

    sampled_sets = [('last', 'non_match')]
    for ref_key, new_key in sampled_sets:
        samples = reference_sets[ref_key].aggregate(
            [{'$sample' : {'size' : n_pairs}},
             {'$unwind' : '$ids'},
             {'$bucketAuto' : {'groupBy' : '$_id', 'buckets' : n_pairs // 2,
                 'output'   : {'ids' : {'$push' : '$ids'},
                               'authors': {'$push' : '$authors'}
                     }}}
             ]
        )
        reference_sets[new_key].insert_many(samples)

    ''' Create the mixed name set?
    reference_sets['last'] IS the mixed-name set, we need to do pairwise comparison on all pairs of IDs within this set'''
