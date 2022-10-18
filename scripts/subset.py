from pymongo import MongoClient
from rich.pretty import pprint
from bson.son import SON
import itertools

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html

def create_mesh_coauthor_match_set(reference_sets):
   for group_doc in reference_sets['first_initial_last_name'].find():
       group = group_doc['group']
       new_groups = []
       for summary in group:
           if summary['mesh'] == '':
               continue # exclude from matching
           found = False
           for new_group in new_groups:
               for new_summary in new_group: # Ah yes nest it deep
                   shared_mesh = set(new_summary['mesh']) & set(summary['mesh'])
                   shared_authors = (set(new_summary['authors']) &
                                     set(summary['authors']))
                   try:
                       shared_authors = ({new_summary['authors']['key']} &
                                         {summary['authors']['key']})
                   except Exception as e:
                       pprint(summary)
                       pprint(new_summary)
                       raise

                   if len(shared_mesh) >= 2 and len(shared_authors) >= 2:
                       new_group.append(summary); found = True
                       break
           if not found:
               new_groups.append([summary])
       group_doc.pop('_id')
       new_groups = [group_doc | dict(group=new_group) for new_group in new_groups]
       yield from new_groups

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

    criteria = {
            'last_name' : ('last',),
            'first_initial_last_name' : ('first_initial', 'last'),
            'full_name' : ('first', 'middle_initial', 'last', 'suffix'), # seems more robust
    }

    push_group = {'group' : {'$push' : {'title' : '$title',
                                        'authors' : '$authors',
                                        'mesh' : '$mesh',
                                        'ids' : '$_id'}}}

    for name, fields in criteria.items():
        pipeline = [
            {'$unwind' : '$authors'},
            {'$group': {
                '_id'    : {k : f'$authors.{k}' for k in fields},
                'count'  : {'$sum': 1},
                **push_group,
                }},
            # Sorting will eat all of your memory and make u sad :(
            # {'$sort': SON([('count', -1), ('_id', -1)])}
        ]
        # print(name)
        reference_sets[name].insert_many(articles.aggregate(pipeline, allowDiskUse=True))

    # Check for matches and create the match set separately from mongodb aggregation
    # "soft" rule          : full name matches, including suffix etc
    # "mesh-coauthor" rule : share one or more coauthor names AND two or more MeSH terms
    reference_sets['soft_match'].insert_many(reference_sets['full_name'].find())
    reference_sets['hard_match'].insert_many(create_mesh_coauthor_match_set(reference_sets))
    for m_type in ('hard', 'soft'):
        reference_sets['match'].insert_many(reference_sets[f'{m_type}_match'].find())

    ''' Create non-matching set by sampling articles with different last names '''
    n_pairs = reference_sets['full_name'].count_documents({})

    sampled_sets = [('last_name', 'non_match')]
    for ref_key, new_key in sampled_sets:
        samples = reference_sets[ref_key].aggregate(
            [{'$sample' : {'size' : n_pairs}},
             {'$unwind' : '$group'},
             {'$bucketAuto' : {'groupBy' : '$_id', 'buckets' : n_pairs // 2,
                 'output'   : { 'group' : {'$push' : '$group'}}
                     }}
             ], allowDiskUse=True
        )
        reference_sets[new_key].insert_many(samples)
