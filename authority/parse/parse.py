import xml.etree.ElementTree as ET
import json
import nltk
# nltk.download('all')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import re

from nameparser import HumanName

from rich import print
from rich.pretty import pprint

class IncompleteEntry(Exception):
    pass

NESTED_MAPPING = {
    'front.journal-meta.journal-title-group.journal-title' : 'journal',
    'front.article-meta.pub-date.year' : 'year',
        }

def parse(entry):
    ''' Take a raw JSON article and add stop-worded title and parsed author names '''
    meta = entry['front']['article-meta']
    entry['authors']  = parse_authors(meta)
    entry['title']    = parse_title(meta)
    entry['abstract'] = parse_abstract(meta)
    entry['language'] = parse_language(meta)
    parse_mappings(entry)
    entry['citations'] = parse_citations(entry)
    entry['affiliation'] = ''
    entry['mesh'] = ''
    return entry

def parse_mappings(entry):
    ''' Remap nested keys to top-level keys with NESTED_MAPPING global dict (above) '''
    for k, v in NESTED_MAPPING.items():
        try:
            sub = entry
            for sk in k.split('.'):
                if isinstance(sub, list):
                    # A rather big assumption: we care about the first entry for either journal title or year
                    sub = sub[0]
                sub = sub[sk]
            entry[v] = sub
        except:
            raise IncompleteEntry(f'key {k} could not be remapped to {v}')

lang_split = re.compile('[ -]')
LANG_MAPPING = {'en' : 'eng'} # can expand as needed
def parse_language(meta):
    ''' Attempt to extract the language(s) field from the article if it is present
        and then re-map it according to the LANG_MAPPING dictionary '''
    try:
        langs = lang_split.split(meta['custom-meta-group']['custom-meta']['meta-value'])
    except KeyError:
        pprint(meta)
        print('No language detected!!')
        # 1/0 # If the language is missing, then use google translate API to detect it
        # https://stackoverflow.com/questions/39142778/how-to-determine-the-language-of-a-piece-of-text
        # langs = ['eng'] # A rather big assumption: non-labelled articles are in english?
        langs = []
    langs = [LANG_MAPPING.get(k, k) for k in langs]
    return langs

def parse_title(meta):
    ''' parse the title of a JSTOR article in JSON form, from metadata '''
    title = None
    try:
        title = meta['title-group']['article-title']
        if isinstance(title, dict):

            title = title.get('#text', title.get('italic'))
        if title is None:
            raise IncompleteEntry('bad title')
    except KeyError:
        raise IncompleteEntry('bad title')
    if title is None:
        raise IncompleteEntry('no title')
    return remove_stop_words(title)

def parse_abstract(meta):
    ''' parse the abstract of a JSTOR article in JSON form, from metadata '''
    try:
        abstract = meta['abstract']['p']
        if isinstance(abstract, dict):
            abstract = abstract['#text']
        elif isinstance(abstract, list):
            abstract = '\n'.join(
                    element if not isinstance(element, dict) else element['#text']
                    for element in abstract)
        return remove_stop_words(abstract)
    except (KeyError, TypeError):
        # raise IncompleteEntry('no abstract')
        # Since many articles are without abstracts, allow this to be empty.
        return '' # Not all articles have abstracts, best way to handle this?


def parse_authors(meta):
    ''' parse the author data of an article into a common format,
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
        for i, author in enumerate(contrib):
            try:
                name   = author['string-name']
                authors.append(parse_name(name, i))
            except KeyError:
                pass # This is an acceptable parsing error
                # that occurs only when an *organization* authors a paper,
                # and not individuals, which excludes it from authority
                # print('bad author name')
                # pprint(author)
        if not authors:
            raise IncompleteEntry('bad author name(s)')
    return authors

suffix_pattern   = re.compile('^([IVX]|(jr)|(sr))+$')
name_sep_pattern = re.compile('[ .,]+')

def filter_empty(elements):
    return (el for el in elements if el != '')

def parse_name(name, order):
    ''' parse the name data for a single author into a common format,
        accounting for edge cases '''
    if isinstance(name, dict): # If name split is annotated
        given = name.get('given-names', '')
        if isinstance(given, list): # When nicknames are present
            # Filter parentheses, then select the first name without them.
            given = [name for name in given if '(' not in name][0]
        elif isinstance(given, dict):
            given = given['#text']
        try:
            last = name['surname']
        except KeyError:
            raise IncompleteEntry(f'no surname: {name}')
        suffix = name.get('suffix', '')

        try:
            first, *mid = name_sep_pattern.split(given)
        except TypeError:
            print('bad name split')
            pprint(name)
            raise IncompleteEntry('bad name split')
    else: # If the name split is unannotated
        try:
            first, *mid, last = filter_empty(name_sep_pattern.split(name))
            if suffix_pattern.match(last.lower()):
                suffix = last
                *mid, last = mid
            else:
                suffix = ''
        except (ValueError, TypeError) as e:
            raise IncompleteEntry(f'incomplete name {name}')
    return construct_name(first, mid, last, suffix, order)

def initial(name):
    return name[0].lower() if len(name) > 0 else ''

def construct_name(first, mid, last, suffix, order):
    first_initial = initial(first)
    middle = ' '.join(mid)

    try:
        first  = first.lower().strip()
        middle = middle.lower().strip()
        last   = last.lower().strip()
    except AttributeError as e:
        raise IncompleteEntry(last)

    return dict(key=f'{first_initial}{last}',
                first_initial=first_initial,
                middle_initial=initial(middle),
                last_initial=initial(last),
                first=first, middle=middle, last=last,
                full=' '.join((c for c in (first, middle, last, suffix)
                               if len(c) > 0)
                               ).title().strip(),
                suffix=suffix.lower().strip(),
                order=order)

# TODO move these into a file, establish them from data, etc?
stop_words_by_field = dict(
    default=set(stopwords.words('english')),
    mesh=["human","male","female","animal","adult","support non-u.s. gov’t","middle age","aged","english abstract","support u.s. gov’t p.h.s.","case report","rats","comparative study","adolescence","child","mice","time factors","child preschool","pregnancy","united states","infant","molecular sequencedata","kinetics","support u.s. gov’t non-p.h.s.","infant newborn"],
    affiliation=set.union(set(stopwords.words('english')),
        set(["university","medicine","medical","usa","hospital","school","institute","center","research","science","college","health","new","laboratory","division","national"])))

def remove_stop_words(words_or_text, field='default'):
    ''' Remove stop words from either a string or list of words, returning either a string or a generator
        The field keyword argument controls which stopwords are used. '''
    is_text    = isinstance(words_or_text, str)
    stop_words = stop_words_by_field[field]
    words      = word_tokenize(words_or_text.lower()) if is_text else words_or_text
    filtered   = (word for word in words if word not in stop_words and len(word) > 1 and word.isalnum())

    if is_text:
        return ' '.join(filtered)
    else:
        return filtered

# https://stackoverflow.com/questions/60391831/python-splitting-year-number-in-brackets-in-a-string-using-regex
# https://stackoverflow.com/questions/6711971/regular-expressions-match-anything
author     = r'a-zA-zÀ-ÿ,\.\&\'\- \(\);'
author_re  = fr'(?P<authors>([{author}\n]*))'
authorn_re = fr'(?P<authors>([{author}]*))'
year_re    = r'\(?(?P<year>\d\d\d\d)\)?:?\.?'
title_re   = r'(?P<title>([^\.]*))'
other      = r'(?P<other>([.*?]*))'
sep_re     = r'[;,&]|( and )'
sep        = re.compile(sep_re)

mid_year_citation_regex  = re.compile(fr'{author_re}{year_re}{title_re}\.{other}')
post_year_citation_regex = re.compile(fr'{authorn_re}\n{title_re}{other}{year_re}\.')

def parse_cited_name(name):
    # Swap order so that initial is always considered the first
    if len(name.last.replace('.', '')) <= 3:
        last  = name.first
        first = name.last
    else:
        last  = name.last
        first = name.first
    return {'surname': last,
            'middle' : name.middle,
            'given-names'  : first,
            'suffix' : name.suffix}

class CitationParseFailure(RuntimeError):
    pass

def parse_citation(citation):
    for citation_regex in (mid_year_citation_regex, post_year_citation_regex):
        result = citation_regex.match(citation)
        if result is not None:
            break
    else:
        raise CitationParseFailure(citation)
    authors_parsed = result.group('authors').replace('(', '').replace('\n', ' ')
    print('Regex parsed:')
    print(authors_parsed)
    components = [c for c in re.split(sep, authors_parsed) if c is not None]
    print('components')
    print(components)
    authors = [HumanName(c) for c in components]
    authors = [h for h in authors if h.first != '' and h.last != '']
    print('human names')
    print(authors)
    authors = [parse_name(parse_cited_name(name), i)
               for i, name in enumerate(authors)]
    authors = [a for a in authors if a['last'].strip() != '']
    pprint(authors)
    return dict(title=remove_stop_words(result.group('title')),
                authors=authors, year=int(result.group('year')))

def parse_citations(article):
    failures = 0
    length   = 0
    last_failure = None
    citations = []
    try:
        for ref in article['back']['ref-list']['ref']:
            try:
                citation = ref['mixed-citation']
                length += 1
                if '#text' in citation:
                    citations.append(parse_citation(citation['#text']))
            except CitationParseFailure as e:
                # print(f'CitationParseFailure: {e}')
                failures += 1
                last_failure = str(e)
                # raise
            except TypeError:
                pass
            except KeyError as e:
                key = str(e).replace('\'', '')
                if key not in {'mixed-citation'}:
                    raise
        if length > 0 and failures > 0:
            # print(f'{failures}/{length} failures')
            if length == failures:
                print('ALL citations failed to parse, indicating a new format:')
                print(f'CitationParseFailure: {last_failure}')
    except KeyError as e:
        key = str(e).replace('\'', '')
        if key not in {'back', 'ref-list', 'ref'}:
            raise
        else:
            pass
            # print(f'No citations {e}')
    except TypeError:
        pass
    return citations
