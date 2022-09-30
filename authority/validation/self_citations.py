from rich.pretty   import pprint
from rich.progress import track
from collections import defaultdict
import re

from authority.process.process import remove_stop_words, process_name

# TODO move this into the process module
# and parse citations when articles are ADDED
# https://stackoverflow.com/questions/60391831/python-splitting-year-number-in-brackets-in-a-string-using-regex
# https://stackoverflow.com/questions/6711971/regular-expressions-match-anything
author_re = r'(?P<authors>([a-zA-Z\. ]*))'
year_re   = r'(?P<year>\d\d\d\d)'
title_re  = r'(?P<title>([a-zA-Z ]*))'
other     = r'(?P<other>([.*?]*))'

citation_regex = re.compile(fr'{author_re}{year_re}\.{title_re}\.{other}')

def reorder_name(name):
    try:
        surname, *mid, initial = name.split(' ')
        return dict(surname=surname, given=initial)
    except ValueError:
        return dict(surname=name)

def parse_citation(citation):
    result = citation_regex.match(citation)
    if result is None:
        raise KeyError
    authors = result.group('authors').split(',')
    authors = [process_name(reorder_name(name), i)
               for i, name in enumerate(authors)]
    return dict(title=remove_stop_words(result.group('title')),
                authors=authors, year=int(result.group('year')))

def parse_citations(article):
    citations = []
    try:
        for ref in article['back']['ref-list']['ref']:
            citation = ref['mixed-citation']
            if '#text' in citation:
                citations.append(parse_citation(citation['#text']))
    except (KeyError, TypeError): # Missing citations
        pass
    return citations

# testing
# parse_citation('L. Saldyt 2022. Title. Other stuff \n here')

def self_citations(blocks, articles):
    ''' Extract clusters based on self-citations '''
    total = blocks.count_documents({})
    for block in track(blocks.find(), total=total):
        self_cites = defaultdict(set)
        for entry in block['group']:
            last      = entry['authors']['last']
            article   = articles.find_one({'_id' : entry['ids']})
            citations = parse_citations(article)

            for citation in citations:
                for author in citation['authors']:
                    if author['last'] == last:
                        self_cites[citation['title']].add(
                            (entry['title'], entry['authors']['last'], str(entry['ids'])))
                        break
        if len(self_cites) > 0:
            yield self_cites
