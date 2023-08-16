
from rich.pretty import pprint
from rich.progress import track
from bson.son import SON
import itertools
import math

from resolution.database.client import get_client

# See this reference on MongoDB aggregation:
# https://pymongo.readthedocs.io/en/stable/examples/aggregation.html
# https://www.mongodb.com/docs/manual/reference/operator/aggregation/match/

def create_mesh_coauthor_match_set(reference_sets):
   total = reference_sets['first_initial_last_name'].count_documents({})
   print(f'checking groups from {total} total groups in FILN set')
   for group_doc in reference_sets['first_initial_last_name'].find():
       group = group_doc['group']
       new_groups = []
       for summary in group:
           assert summary['mesh'] != '', 'MeSH needs to be present, filtering done before this step'
           found = False
           for new_group in new_groups:
               for new_summary in new_group:
                   shared_mesh    = (set(new_summary['mesh']) &
                                     set(summary['mesh']))
                   a_authors = new_summary['coauthors']
                   b_authors = summary['coauthors']
                   # VERIFIED working :)
                   shared_authors = (set(auth['key'] for auth in a_authors) &
                                     set(auth['key'] for auth in b_authors))
                   if len(shared_mesh) >= 2 and len(shared_authors) >= 3: # must be 3 since original author is included too
                       new_group.append(summary); found = True
                       break
           if not found:
               new_groups.append([summary])
       group_doc['group_id'] = group_doc.pop('_id')
       new_groups = [new_group for new_group in new_groups if len(new_group) > 1] # filter
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
        SF = Suffix

    Entailing:
        matches: FI-MI-LN-SF
        blocks:  FI-LN
        As well as all other combinations of these

    Keep in mind that the eventual goal is to fill out the r-table uniformly
    '''
    client = get_client('mongo_credentials.json', local=True)
    jstor_database = client.jstor_database
    articles       = jstor_database.articles

    # client.drop_database('reference_sets')
    reference_sets = client.reference_sets

    # ''' Create matching based on different criteria '''

    criteria = {
            'first_initial_last_name' : ('first_initial', 'last'),
            'full_name' : ('first', 'middle_initial', 'last', 'suffix'), # Check suffix and middle initial, but do not ensure they are present
            'initials_last_suffix' : ('first_initial', 'middle_initial', 'last', 'suffix'), # seems more robust
    }

    attributes = ['authors', 'coauthors', 'title', 'language', 'journal', 'mesh', 'affiliation']
    push_group = {'group' : {'$push' : {**{attr : f'${attr}' for attr in attributes}, 'ids' : '$_id'}}}

    for name, fields in criteria.items():
        reference_sets.drop_collection(name)
        pipeline = [
            {'$match': {'mesh': {'$ne': ''}}},      # filter by MeSH presence
            {'$set'  : {'coauthors' : '$authors'}}, # copy coauthor info
            {'$unwind' : '$authors'},
            {'$group': {
                '_id'    : {k : f'$authors.{k}' for k in fields},
                'count'  : {'$sum': 1},
                **push_group,
                }},
            # Sorting can eat all of your memory and make u sad :(
            # {'$sort': SON([('count', -1), ('_id', -1)])}
        ]
        print(f'Subsetting for {name}')
        reference_sets[name].insert_many(articles.aggregate(pipeline, allowDiskUse=True))

    # Check for matches and create the match set separately from mongodb aggregation
    # "name" rule          : full name matches, including suffix etc
    # "mesh-coauthor" rule : share one or more coauthor names AND two or more MeSH terms
    reference_sets.drop_collection('name_match')
    reference_sets['name_match'].insert_many(reference_sets['initials_last_suffix'].find(
        {'_id.middle_initial' : {'$ne' : ''},
         '_id.suffix'         : {'$ne' : ''}
            })) # Technically also drops names with multiple middle initials
    reference_sets.drop_collection('mesh_coauthor_match')
    reference_sets['mesh_coauthor_match'].insert_many(create_mesh_coauthor_match_set(reference_sets))
