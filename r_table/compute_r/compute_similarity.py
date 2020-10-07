import mysql.connector
import json
import argparse

import sys
sys.path.append('../')
from SQL.SQLClient import SQLClient

def compute_x1(match):
    fullname1 = match[rowheadings['fullname1']]
    fullname2 = match[rowheadings['fullname2']]
    coautha = match[rowheadings['authors1']]
    coauthb = match[rowheadings['authors2']]
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')

    if(coauth1 is not None and coauth2 is not None and fullname1 != fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))
    if(coauth1 is not None and coauth2 is not None and fullname1 == fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))-1
    else:
        coauth_intersection = 0
    if(coauth_intersection < 2):
        is_match_set = False
        # print(fullname1+" "+fullname2)
        # print(str(coauth1)+"   "+str(coauth2))
    else:
        is_match_set = True

    init2a = match[rowheadings['middle_initial1']]
    init2b = match[rowheadings['middle_initial2']]
    
    if(init2a is None and init2b is None):
        value = 2
    if(init2a is not None and init2b is not None):
        if(init2a == init2b): #todo: mid1 O mid2 Ø fullname1 Arne O. Mooers fullname2 Arne Ø. Mooers
            value = 3
        else:
            value = 0
    if(init2a is None or init2b is None):
        value = 1

    if(value == 0):
        print(str(value)+" value "+ " mid1 "+ init2a+" mid2 "+ init2b +" fullname1 "+ fullname1 + " fullname2 "+ fullname2)
    if(is_match_set):
        if(value in x1_m):
            x1_m[value] += 1
        else:
            x1_m[value] = 1
    else:
        if(value in x1_nm):
            x1_nm[value] += 1
        else:
            x1_nm[value] = 1


def compute_x2(match):
    fullname1 = match[rowheadings['fullname1']]
    fullname2 = match[rowheadings['fullname2']]
    coautha = match[rowheadings['authors1']]
    coauthb = match[rowheadings['authors2']]
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')

    if(coauth1 is not None and coauth2 is not None and fullname1 != fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))
    if(coauth1 is not None and coauth2 is not None and fullname1 == fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))-1
    else:
        coauth_intersection = 0

    if(coauth_intersection < 2):
        is_match_set = False
    else:
        is_match_set = True

    suffa = match[rowheadings['suffix1']]
    suffb = match[rowheadings['suffix2']]

    if(suffa is not None and suffb is not None and suffa == suffb):
        value = 1
    else:
        value = 0
    if(is_match_set):
        if(value in x2_m):
            x2_m[value] += 1
        else:
            x2_m[value] = 1
    else:
        if(value in x2_nm):
            x2_nm[value] += 1
        else:
            x2_nm[value] = 1


def compute_xa(match, is_match_set= True):
    fullname1 = match[rowheadings['fullname1']]
    fullname2 = match[rowheadings['fullname2']]
    coautha = match[rowheadings['authors1']]
    coauthb = match[rowheadings['authors2']]
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')
  
    if(coauth1 is not None and coauth2 is not None and fullname1 != fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))
    if(coauth1 is not None and coauth2 is not None and fullname1 == fullname2):
        coauth_intersection = len(list(set(coauth1) & set(coauth2)))-1
    else:
        coauth_intersection = 0
    
    title1 = match[rowheadings['title1']]
    title2 = match[rowheadings['title2']]
    x3 = len(set(title1.split(' ')) & set(title2.split(' ')))

    if(match[rowheadings['journal_name1']] == match[rowheadings['journal_name2']]):
        x4 = 1
    else:
        x4 = 0
    
    x5 = coauth_intersection

    mesh1 = match[rowheadings['mesh_terms1']].split(',')
    mesh2 = match[rowheadings['mesh_terms2']].split(',')

    x6 = len(list(set(mesh1) & set(mesh2)))

    # langa = match[rowheadings['language1']]
    # langb = match[rowheadings['language2']]
    # if(langa == langb and langa != 'eng'):
    #     x7 = 3
    # if(langa == langb and langa == 'eng'):
    #     x7 = 2
    # if(langa != langb and (langa == 'eng' or langb == 'eng')):
    #     x7 = 1
    # else:
    #     x7 = 0
    
    value = str([x3, x4, x5, x6])
    if(is_match_set):
        if(value in xa_m):
            xa_m[value] += 1
        else:
            xa_m[value] = 1
    else:
        if(value in xa_nm):
            xa_nm[value] += 1
        else:
            xa_nm[value] = 1
    

#todo: mark view row as completed after compute_xa(match)
def compute_xa_allmatches():
    count = get_article_match_set_pair_count()
    offset = 0
    while(offset < count):
        # article_match_set = sql_client.execute_and_fetch('select * from article_match')
        article_match_set = sql_client.execute_and_fetch('select * from article_match'+
        ' limit ' + str(limit) + ' offset ' + str(offset))

        for match in article_match_set:
            try:
                compute_xa(match, True)
                # mark_as_done(match, 'article_match')
            except Exception as e:
                print(e)


    with open('xa_m.json', 'w') as fp:
        json.dump(xa_m, fp)


def compute_xa_allnonmatches():
    count = get_article_non_match_set_pair_count()
    offset = 0
    while(offset < count):
        query = 'select * from article_non_match'
        # print(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        article_non_match_set = sql_client.execute_and_fetch(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        
        for match in article_non_match_set:
            try:
                compute_xa(match, False)
                # mark_as_done(match, 'article_non_match')
            except Exception as e:
                print(e)
        offset += limit


    with open('xa_nm.json', 'w') as fp:
        json.dump(xa_nm, fp)
    

def compute_x1_x2_all():
    count = get_name_set_pair_count()
    offset = 0
    while(offset < count):
        name_set = sql_client.execute_and_fetch('select * from name_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))

        for match in name_set:
            try:
                compute_x1(match)
                compute_x2(match)
                # mark_as_done(match, 'name_set')
            except Exception as e:
                print(e)
        offset+=limit

    

    with open('x1_m.json', 'w') as fp:
        json.dump(x1_m, fp)
    with open('x1_nm.json', 'w') as fp:
        json.dump(x1_nm, fp)
    with open('x2_m.json', 'w') as fp:
        json.dump(x2_m, fp)
    with open('x2_nm.json', 'w') as fp:
        json.dump(x2_nm, fp)


def mark_as_done(record, table):
    query = 'update ' + table + ' set iscomputed=\'True\' where id1 =' + record[rowheadings['id1']] + ' and position1 =' + str(record[rowheadings['position1']]) + ' and id2 = '+ record[rowheadings['id2']] + ' and position2 = ' + str(record[rowheadings['position2']])
    sql_client.execute(query)


#parse command line arguments. usage: python .\compute_similarity.py --udpate True --min 0 --max 100000 --x1 True --x2 True --xa True
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", help="True if updating existing similarity scores. False otherwise", required=True)
    parser.add_argument("--limit", help="no. of pairs to process", required=True)
    parser.add_argument("--offset", help="process from pair number", required=True)
    args = parser.parse_args()
    update = args.update
    limit = args.limit
    offset = args.offset
    return update, limit, offset


def get_name_set_pair_count():
    query = 'select count(*) from name_set'
    count = sql_client.execute_and_fetch(query)
    print("name set pair count: "+str(count))
    return count


def get_article_match_set_pair_count():
    query = 'select count(*) from article_match'
    count = sql_client.execute_and_fetch(query)
    print("article match set pair count: "+str(count))
    return count


def get_article_non_match_set_pair_count():
    query = 'select count(*) from article_non_match'
    count = sql_client.execute_and_fetch(query)
    print("article non match set pair count: "+str(count))
    return count


sql_client = SQLClient()
sql_client.connect_to_db('test1')


rowheadings = {}
rowheadings['id1'] = 0
rowheadings['position1'] = 1
rowheadings['last_name1'] = 2
rowheadings['first_initial1'] = 3
rowheadings['middle_initial1'] = 4
rowheadings['suffix1'] = 5
rowheadings['title1'] = 6
rowheadings['journal_name1'] = 7
rowheadings['first_name1'] = 8
rowheadings['middle_name1'] = 9
rowheadings['fullname1'] = 10
rowheadings['authors1'] = 11
rowheadings['language1'] = 12
rowheadings['mesh_terms1'] = 13
rowheadings['affiliation1'] = 14
rowheadings['id2'] = 15
rowheadings['position2'] = 16
rowheadings['last_name2'] = 17
rowheadings['first_initial2'] = 18
rowheadings['middle_initial2'] = 19
rowheadings['suffix2'] = 20
rowheadings['title2'] = 21
rowheadings['journal_name2'] = 22
rowheadings['first_name2'] = 23
rowheadings['middle_name2'] = 24
rowheadings['fullname2'] = 25
rowheadings['authors2'] = 26
rowheadings['language2'] = 27
rowheadings['mesh_terms2'] = 28
rowheadings['affiliation2'] = 29


# update, limit, offset = parse_arguments()
update = 'false'
limit = 9000000

if update.lower() == 'true':
    with open('x1_m.json') as json_file: 
        x1_m = json.load(json_file) 
    with open('x1_nm.json') as json_file: 
        x1_nm = json.load(json_file) 
    with open('x2_m.json') as json_file: 
        x2_m = json.load(json_file) 
    with open('xa_m.json') as json_file: 
        xa_m = json.load(json_file) 
    with open('xa_nm.json') as json_file: 
        xa_nm = json.load(json_file) 
    with open('x2_nm.json') as json_file: 
        x2_nm = json.load(json_file) 

else:
    x1_m = {}
    x1_nm = {}

    x2_m = {}
    x2_nm = {}

    xa_m = {}
    xa_nm = {}

get_name_set_pair_count()
get_article_match_set_pair_count()
get_article_non_match_set_pair_count()

# # compute_xa_allmatches()
# compute_xa_allnonmatches()
# # compute_x1_x2_all()
