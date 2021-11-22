import traceback
import xml.etree.ElementTree as ET 
from collections import Counter
from zipfile import ZipFile
import time
import os
import json
import nltk
# nltk.download('all')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import mysql.connector
import re
import requests

from models.Article import Article
from models.Author import Author


def get_authors(article_meta):
    contrib_group = article_meta.find('./contrib-group')
    author_list = []
    author_name_list = []

    article_record_list = []
    if contrib_group is not None:
        string_names = contrib_group.findall('./contrib')
        for name in string_names:
            given_name = name.find('./string-name/given-names')
            surname = name.find('./string-name/surname')
            suffix = name.find('./string-name/suffix')

            string_name = name.find('./string-name')
            fullname = ""
            author = None
            if(given_name is not None and surname is not None):
                given_name_list = given_name.text.split(" ")
                middle_name = " ".join(given_name_list[1:]).replace(',','')
                given_name = given_name_list[0].replace(',','')
                surname = surname.text.replace(',','')
                fullname = given_name + " "+ middle_name +" "+ surname 
                if suffix is not None:
                    suffix = suffix.text.replace(',','')
                    fullname += " "+ suffix
                else:
                    suffix = ""
                author = Author(given_name, middle_name, surname, suffix, fullname)

            if(given_name is None and surname is None and string_name is not None):
                fullname = string_name.text.replace(',', '')
                given_name, middle_name, surname, suffix = parse_name(fullname)
                author = Author(given_name, middle_name, surname, suffix, fullname)
                

            if author is not None:
                author_list.append(author)
                author_name_list.append(fullname)

    return author_list, author_name_list


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
        article_record_list.append(Article(unique_id, i, author.surname, first_initial, middle_initial, author.suffix, article_title_processed, journal_name, author.full_name, author.given_name, author.middle_name, language, ",".join(author_name_list), article_title, year))
        i+=1
    return article_record_list


def parse_name(name):
    suffix_pattern = re.compile('\s[IVX][IVX]+')
    name = name.strip().replace(',','')
    name_split = name.split(' ')
    name_size = len(name_split)
    if(name_size < 2):
        print(name + "no last/first name")
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
            i=1
            for i in range(1, name_size-2):
                middle += name_split[i]+" "
            return name_split[0], middle, name_split[name_size-2], name_split[name_size-1]
        else:
            middle = ''
            i=1
            for i in range(1, name_size-1):
                middle += name_split[i]+" "
            return name_split[0], middle, name_split[name_size-1], '' 


def remove_stop_words(text, field):
    text = text.lower()
    stop_words = []
    #todo: consider other languages too
    if field == 'title':
        stop_words = set(stopwords.words('english'))
    elif field == 'mesh':
        stop_words = ["human","male","female","animal","adult","support non-u.s. gov’t","middle age","aged","english abstract","support u.s. gov’t p.h.s.","case report","rats","comparative study","adolescence","child","mice","time factors","child preschool","pregnancy","united states","infant","molecular sequencedata","kinetics","support u.s. gov’t non-p.h.s.","infant newborn"]
    elif field == "affiliation":
        affiliation_stop_words = ["university","medicine","medical","usa","hospital","school","institute","center","research","science","college","health","new","laboratory","division","national"]
        stop_words = set.union(set(stopwords.words('english')), set(affiliation_stop_words))
    word_tokens = word_tokenize(text) 
    filtered_sentence = []
    for word in word_tokens:
        if(word not in stop_words and len(word)>1 and word.isalnum()):
            filtered_sentence.append(word)
    final_sentence = '' 
  
    for w in filtered_sentence: 
        final_sentence += w + " "
    return final_sentence


def add_to_mesh_input_file(unique_id, abstract, mesh_filename):
    if(abstract is not None):
        abstract_text = abstract.text
        if abstract_text != "":
            value = (abstract_text.encode("ascii", "ignore")).decode("utf-8")
            with open(mesh_filename, "a+") as f:
                f.write(unique_id+'|'+value)
                f.write('\n')