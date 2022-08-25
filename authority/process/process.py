import xml.etree.ElementTree as ET
import json
import nltk
# nltk.download('all')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

from rich.pretty import pprint

class IncompleteEntry(Exception):
    pass

def process(entry):
    ''' Take a raw JSON article and add stop-worded title and processed author names '''
    meta = entry['front']['article-meta']
    entry['authors']  = process_authors(meta)
    entry['title']    = process_title(meta)
    entry['abstract'] = process_abstract(meta)
    return entry

def process_title(meta):
    ''' Process the title of a JSTOR article in JSON form, from metadata '''
    title = meta['title-group']['article-title']
    if isinstance(title, dict):
        title = title['#text']
    if title is None:
        raise IncompleteEntry('no title')
    return remove_stop_words(title)

def process_abstract(meta):
    ''' Process the abstract of a JSTOR article in JSON form, from metadata '''
    try:
        abstract = meta['abstract']['p']
        if isinstance(abstract, dict):
            abstract = abstract['#text']
        elif isinstance(abstract, list):
            abstract = '\n'.join(
                    element if not isinstance(element, dict) else element['#text']
                    for element in abstract)
        return remove_stop_words(abstract)
    except KeyError:
        # raise IncompleteEntry('no abstract')
        # Since many articles are without abstracts, allow this to be empty.
        return '' # Not all articles have abstracts, best way to handle this?


def process_authors(meta):
    ''' Process the author data of an article into a common format,
        accounting for edge cases'''
    try:
        groups = meta['contrib-group']
    except KeyError:
        raise IncompleteEntry(f'no author data') # How best to handle this?
    if isinstance(groups, dict): # Typical case where only one contrib group
        groups = [groups]        # General case with multiple possible contrib
    for group in groups:
        contrib = group['contrib']
        authors = []
        if not isinstance(contrib, list): # Edge case for single-author papers
            contrib = [contrib]
        for author in contrib:
            name   = author['string-name']
            authors.append(process_name(name))
    return authors

suffix_pattern   = re.compile('([IVX]|(jr)|(sr))+')
name_sep_pattern = re.compile('[ .,]+')

def process_name(name):
    ''' Process the name data for a single author into a common format,
        accounting for edge cases '''
    if isinstance(name, dict): # If name split is annotated
        given   = name.get('given-names', '')
        last    = name['surname']
        suffix  = name.get('suffix', '')
        first, *mid = name_sep_pattern.split(given)
    else: # If the name split is unannotated
        try:
            first, *mid, last = name_sep_pattern.split(name)
            if suffix_pattern.match(last):
                suffix = last
                *mid, last = mid
            else:
                suffix = ''
        except ValueError:
            raise IncompleteEntry(f'incomplete name {name}')
    return construct_name(first, mid, last, suffix)

def construct_name(first, mid, last, suffix):
    first_initial = first[0].lower() if len(first) > 0 else ''
    middle = ' '.join(mid)

    first  = first.lower().strip()
    middle = middle.lower().strip()
    last   = last.lower().strip()

    return dict(key=f'{first_initial}{last}', first_initial=first_initial,
                first=first, middle=middle, last=last,
                full=' '.join((first, middle, last, suffix)).title(),
                suffix=suffix)


stop_words_by_field = dict(
    default=set(stopwords.words('english')),
    mesh=["human","male","female","animal","adult","support non-u.s. gov’t","middle age","aged","english abstract","support u.s. gov’t p.h.s.","case report","rats","comparative study","adolescence","child","mice","time factors","child preschool","pregnancy","united states","infant","molecular sequencedata","kinetics","support u.s. gov’t non-p.h.s.","infant newborn"],
    affiliation=set.union(set(stopwords.words('english')),
        set(["university","medicine","medical","usa","hospital","school","institute","center","research","science","college","health","new","laboratory","division","national"])))

def remove_stop_words(text, field='default'):
    stop_words = stop_words_by_field[field]
    filtered = ' '.join(word for word in word_tokenize(text.lower())
                        if word not in stop_words and len(word) > 1 and word.isalnum())
    return filtered
