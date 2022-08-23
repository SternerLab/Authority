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
    title = meta['title-group']['article-title']
    if isinstance(title, dict):
        title = title['#text']
    if title is None:
        raise IncompleteEntry('no title')
    return remove_stop_words(title)

def process_abstract(meta):
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

def process_name(name):
    ''' Process the name data for a single author into a common format,
        accounting for edge cases '''
    if isinstance(name, dict): # If name split is annotated
        given   = name.get('given-names', '')
        last    = name['surname']
        first, *mid = re.split('[ .,]+', given)
    else: # If the name split is unannotated
        try:
            first, *mid, last = re.split('[ .,]+', name)
        except ValueError:
            raise IncompleteEntry(f'incomplete name {name}')

    first_initial = first[0].lower() if len(first) > 0 else ''
    middle = ' '.join(mid)
    return dict(key=f'{first_initial}{last.lower()}',
                first_initial=first_initial,
                first=first.lower(),
                middle=middle.lower(),
                last=last.lower())


stop_words_by_field = dict(
    default=set(stopwords.words('english')),
    mesh=["human","male","female","animal","adult","support non-u.s. gov’t","middle age","aged","english abstract","support u.s. gov’t p.h.s.","case report","rats","comparative study","adolescence","child","mice","time factors","child preschool","pregnancy","united states","infant","molecular sequencedata","kinetics","support u.s. gov’t non-p.h.s.","infant newborn"],
    affiliation=set.union(set(stopwords.words('english')),
        set(["university","medicine","medical","usa","hospital","school","institute","center","research","science","college","health","new","laboratory","division","national"])))

def remove_stop_words(text, field='default'):
    stop_words = stop_words_by_field[field]
    filtered = ' '.join(word for word in word_tokenize(text.lower())
                        if word not in stop_words and len(word) > 1 and word.isalnum())


'''
def add_to_mesh_input_file(unique_id, abstract, mesh_filename):
    if(abstract is not None):
        abstract_text = abstract.text
        if abstract_text != "":
            value = (abstract_text.encode("ascii", "ignore")).decode("utf-8")
            with open(mesh_filename, "a+") as f:
                f.write(unique_id+'|'+value)
                f.write('\n')

def parse(xmlfile, mesh_file):
    tree = ET.parse(xmlfile)
    article = tree.getroot()
    article_meta = article.find('./front/article-meta')

    article_title = article_meta.find('./title-group/article-title').text
    abstract = article_meta.find('./abstract/p')
    unique_id = article_meta.find('./article-id').text

    add_to_mesh_input_file(unique_id,abstract, mesh_file)

    article_title_processed = remove_stop_words(article_title, 'title')

    journal_meta = article.find('./front/journal-meta')
    journal_name = journal_meta.find('./journal-title-group/journal-title').text
    year = int(article_meta.find('./pub-date/year').text)

    language = ''
    custom_meta_group = article_meta.find('./custom-meta-group')
    if custom_meta_group is not None:
        custom_meta = custom_meta_group.find('./custom-meta')
        language = custom_meta.find('meta-value').text

    author_list, author_name_list = get_authors(article_meta)
    article_record_list = []
    i = 1
    for author in author_list:
        first_initial = '' if len(author.given_name) == 0 else author.given_name[0]
        middle_initial = '' if len(author.middle_name) == 0 else author.middle_name[0]
        article_record_list.append(Article(unique_id, i, author.surname, first_initial, middle_initial, author.suffix, article_title_processed, journal_name, author.full_name, author.given_name, author.middle_name, language, ",".join(author_name_list), "", "", article_title, year))
        i+=1
    return article_record_list

def parse_name(name):
    suffix_pattern = re.compile('\s[IVX][IVX]+')
    name = name.strip().replace(',','')
    name_split = name.split(' ')
    name_size = len(name_split)
    if(name_size < 2):
        print(f'{name}: no last/first name')
        return '','',name,''
    if(name_size == 2):
        return name_split[0],'',name_split[1],''
    if(name_size == 3):
        if(name_split[2] == "Jr." or name_split[2] == "Sr." or suffix_pattern.match(name_split[2])):
            return name_split[0],'',name_split[1], name_split[2]
        else:
            return name_split[0],name_split[1], name_split[2], ''
    else:
        if(name_split[name_size-1] == "Jr." or name_split[name_size-1] == "Sr." or suffix_pattern.match(name_split[name_size-1])):
            middle = ''
            for i in range(1, name_size-2):
                middle += name_split[i]+" "
            return name_split[0], middle, name_split[name_size-2], name_split[name_size-1]
        else:
            middle = ''
            for i in range(1, name_size-1):
                middle += name_split[i]+" "
            return name_split[0], middle, name_split[name_size-1], ''

'''
