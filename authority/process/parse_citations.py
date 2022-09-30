import re

from authority.process.process import remove_stop_words, process_name

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
