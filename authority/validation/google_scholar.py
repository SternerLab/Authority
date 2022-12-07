from scholarly import scholarly as scholar
import scholarly
import itertools
from rich.pretty import pprint
import re

from ..parse.parse import parse_name, construct_name, remove_stop_words

from .resolver import Resolver

class GoogleScholarResolver(Resolver):
    ''' A specialized class for resolving labels for author clusters
        To be specifically used by google scholar '''
    def __init__(self, client, name):
        self.name  = name
        self.cache = None
        self.collection = client.validation[name + '_dois']

    def resolve(self, cluster):
        gid = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'

        reference_clusters = []
        resolved = 0
        for doc in self.collection.find({'author.key' : key}):
            reference_clusters.append([str(_id) for _id in doc['mongo_ids']])
            resolved += 1
        # if resolved > 0:
        #     print('resolved', resolved)
        return reference_clusters

    def build_cache(self):
        pass

scholar.set_timeout(5)

pg = scholarly.ProxyGenerator()
scholar.use_proxy(pg)

def title_words_iou_score(words_a, words_b):
    return len(words_a & words_b) / len(words_a | words_b)

def title_close_match(a, b, threshold=2):
    ''' Check if two titles match within a threshold of n words,
        not accounting for ordering of words! '''
    if threshold == 0:
        return a == b
    else:
        words_a = set(a.split(' '))
        words_b = set(b.split(' '))
        base    = max(len(words_a), len(words_b))
        if base <= threshold:
            return False
        iou_threshold = (base - threshold) / base
        score = title_words_iou_score(words_a, words_b)
        return score > iou_threshold

def parse_google_scholar_name(name, order=1):
    ''' parse a name in the Google Scholar format into the common format used in
        mongodb for JSTOR'''
    components = re.split('[ .,]+', name)
    if len(components) == 1:
        name = components[0]
        first = ''
        last = name
        mid = ''
    else:
        first, *last = components
        if len(first) == 2:
            first, mid = first
        else:
            mid = ''
        last = ' '.join(last).lower() # Fairly certain scholar puts middle name into initials
    return construct_name(first, mid, last, '', order)

def get_clusters(entry):
    ''' Get labelled clusters for validation, both by author and by title
    In the case of by-author, resolution is done via matching title strings
    In the case of by-title, resolution is done via matching author strings '''
    title = entry['title']
    authors = entry['authors']
    for author in authors:
        pprint(author)
        yield from get_papers_by_author(author, title)
    # yield from get_papers_by_title(title, authors)

def get_papers_by_author(reference_author, reference_title, author_limit=10,
        strict=False):
    ''' Search for an author and resolve their name by matching paper title '''
    query = scholar.search_author(reference_author['full'])
    for author in itertools.islice(query, author_limit):
        name_dict = parse_name(author['name'], order=0)
        scholar.fill(author,
                sections=['basics', 'indices', 'publications', 'coauthors'])
        titles = [remove_stop_words(pub['bib']['title'])
                  for pub in author['publications']]
        if strict:
            title_matches = [title == reference_title for title in titles]
        else:
            title_matches  = [title_close_match(title, reference_title) for title in titles]
        if any(title_matches):
            if not strict:
                titles.append(reference_title) # so that a strict match is guaranteed
            yield dict(scholar_id=author['scholar_id'],
                       author=reference_author, titles=titles)
            break

def get_papers_by_title(reference_title, reference_authors, paper_limit=10, strict=False):
    ''' Search for a paper and resolve it by matching title and author names '''
    pprint(reference_title)
    query = scholar.search_pubs(reference_title)
    for paper in itertools.islice(query, paper_limit):
        title   = remove_stop_words(paper['bib']['title'])
        pprint(title)
        authors = [parse_google_scholar_name(name, order=i)
                   for i, name in enumerate(paper['bib'].get('author', []))]
        pprint(authors)
        author_matches = [a['key'] == b['key']
                          for a, b in zip(authors, reference_authors)]
        pprint(author_matches)
        paper['title']   = title
        paper['authors'] = authors
        if strict:
            title_match = title == reference_title
        else:
            title_match = title_close_match(title, reference_title)
        print(title_match, all(author_matches)) # strict currently
        if title_match and all(author_matches): # strict currently
            scholar.fill(paper)
            pprint(paper['author_id'])
            pprint(paper)
            for author in authors:
                yield dict(author=author, titles=[title])
            # yield dict(author=reference_author, titles=titles)
            break # Should only need one
