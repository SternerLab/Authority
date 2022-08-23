from scholarly import scholarly
import itertools
from rich.pretty import pprint
import pymongo
import re

from ..process.process import process_name, construct_name, remove_stop_words

def process_google_scholar_name(name):
    ''' Process a name in the Google Scholar format into the common format used in
        mongodb for JSTOR'''
    components = re.split('[ .,]+', name)
    if len(components) == 1:
        name = components[0]
    else:
        first, *last = components
        if len(first) == 2:
            first, mid = first
        else:
            mid = ''
        last = ' '.join(last).lower() # Fairly certain scholar puts middle name into initials
    return construct_name(first, mid, last)

def get_clusters(entry):
    ''' Get labelled clusters for validation, both by author and by title
    In the case of by-author, resolution is done via matching title strings
    In the case of by-title, resolution is done via matching author strings '''
    title = entry['title']
    authors = entry['authors']
    for author in authors:
        pprint(author)
        yield from get_papers_by_author(author, title)
    # Leaving this inactive for now
    # yield from get_papers_by_title(title, authors, author_collection)

def get_papers_by_author(reference_author, reference_title, author_limit=10):
    ''' Search for an author and resolve their name by matching paper title '''
    query = scholarly.search_author(reference_author['full'])
    for author in itertools.islice(query, author_limit):
        try:
            # Check if author has been added before, by unique scholar id
            pprint(author)
            name_dict = process_name(author['name'])
            pprint(name_dict)
            scholarly.fill(author,
                    sections=['basics', 'indices', 'publications', 'coauthors'])
            titles = [remove_stop_words(pub['bib']['title'])
                      for pub in author['publications']]
            pprint(titles)
            title_matches = [title == reference_title for title in titles]
            pprint(title_matches)
            if any(title_matches):
                yield dict(author=reference_author, titles=titles)
                break
        except pymongo.errors.DuplicateKeyError: # author is already processed
            pass

# Leaving this inactive for now
# def get_papers_by_title(reference_title, reference_authors,
#                         author_collection, paper_limit=10):
#     ''' Search for a paper and resolve it by matching title and author names '''
#     pprint(reference_title)
#     query = scholarly.search_pubs(reference_title)
#     for paper in itertools.islice(query, paper_limit):
#         title   = remove_stop_words(paper['bib']['title'])
#         authors = [process_google_scholar_name(name)
#                    for name in paper['bib'].get('author', [])]
#         author_matches = [a['key'] == b['key']
#                           for a, b in zip(authors, reference_authors)]
#         paper['title']   = title
#         paper['authors'] = authors
#         if title == reference_title and all(author_matches): # strict currently
#             yield paper
#             # yield dict(author=reference_author, titles=titles)
#             break # Should only need one
