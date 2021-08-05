# import mysql.connector
import json
import argparse

import sys
sys.path.append('../')
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client
import csv


def get_x1_score(init2a, init2b):
    if((init2a == "" and init2b == "")):
        value = 2
    elif((init2a != "" and init2b !="")):
        if(init2a == init2b): #todo: mid1 O mid2 Ø fullname1 Arne O. Mooers fullname2 Arne Ø. Mooers
            value = 3
        else:
            value = 0
    elif(init2a=="" or init2b == ""):
        value = 1
    
    return value


def get_x2_score(suffa, suffb):
    if((suffa !="" and suffb !="" and suffa == suffb)):
        value = 1
    else:
        value = 0
    return value


def get_xa_score(title1, title2, journal_name1, journal_name2, coauth1, coauth2, fullname1, fullname2, mesh1, mesh2, langa, langb):
    x3 = len(list(set(title1.split(' ')) & set(title2.split(' '))))
    if(journal_name1 == journal_name2):
        x4 = 1
    else:
        x4 = 0
    
    coauth_intersection = compute_coauth_intersection(coauth1, coauth2, fullname1, fullname2)
    x5 = coauth_intersection

    x6 = len(list(set(mesh1) & set(mesh2)))

    
    if(set(langa.split(" ")) == set(langb.split(" ")) and (langa != 'eng' or langa!= 'en')):
        x7 = 3
    elif(set(langa.split(" ")) == set(langb.split(" ")) and (langa == 'eng' or langa == 'en')):
        x7 = 2
    elif(set(langa.split(" ")) != set(langb.split(" ")) and (langa == 'eng' or langb == 'eng' or langa == 'en' or langb == 'en' )):
        x7 = 1
    else:
        x7 = 0
    
    return x3,x4,x5,x6,x7


def get_x10_score(firstname1, firstname2):
    score = 0
    hyphen='-'
    firstname1_withoutspace_hyphen = firstname1.replace(" ","")
    firstname1_withoutspace_hyphen = firstname1_withoutspace_hyphen.replace(hyphen,"")
    firstname2_withoutspace_hyphen = firstname2.replace(" ","")
    firstname2_withoutspace_hyphen = firstname2_withoutspace_hyphen.replace(hyphen,"")

    # 11: exact match,
    if(firstname1 == firstname2 and len(firstname1) > 1):
        score = 11

    # 10: namewithorwithouthyphen/space(jean-francoisvs.jeanfrancois or jean-
    # francois vs. jean francois),
    elif(firstname1_withoutspace_hyphen == firstname2_withoutspace_hyphen):
        score = 10

    # 9: hyphenated name vs. name with hyphen and initial (jean-francois vs.
    # jean-f),
    elif(hyphen in firstname1 and hyphen in firstname2):
        if(len(firstname1.split(hyphen)[1]) or len(firstname2.split(hyphen)[1])):
            if (firstname1.split(hyphen)[1][0] == firstname2.split(hyphen)[1][0]):
                score = 9
    # 8: hyphenated name with initial vs. name (jean-f vs. jean),
    elif((hyphen in firstname1 and len(firstname1.split(hyphen)[1])==1) or (hyphen in firstname2 and len(firstname2.split(hyphen)[1])==1)):
        if (firstname1.split(hyphen)[0] == firstname2.split(hyphen)[0]):
            score = 8
    # 7: hyphenated name vs. first name only (jean-francois vs. jean)
    elif(hyphen in firstname1 or hyphen in firstname2):
        if (firstname1.split(hyphen)[0] == firstname2.split(hyphen)[0]):
            score = 7
    # 6: nickname match (dave vs. david)
    elif nickname_match(firstname1, firstname2):
        score = 6
    # 5: oneeditdistance(deletion:bjoernvs.bjorn,replacement:bjoernvs.bjaern,
    # or flip order of two characters: bjoern vs. bjeorn)
    elif oneeditdistance(firstname1,firstname2):
        score = 5
    # 4: name matches first part of other name and length > 2 (zak vs. zakaria) 
    elif (len(firstname1)>2 and len(firstname2)>2 and (firstname1 in firstname2 or firstname2 in firstname1)):
        score = 4
    # 3: name matches first part of other name and length = 2 (th vs. thomas) 
    elif ((len(firstname1)==2 or len(firstname2)==2) and (firstname1 in firstname2 or firstname2 in firstname1)):
        score = 3
    # 2: 3-letter initials match (e.g., jean francois g vs. jfg)
    elif (firstname1==''.join([_name[0] for _name in firstname2.split(' ')]) or firstname2==''.join([_name[0] for _name in firstname1.split(' ')])):
        score = 2
    # 1: same first initial if one of them only has initial given,
    elif (firstname1[0] == firstname2[0] and (len(firstname1) == 1 or len(firstname2) == 1)):
        score = 1
    # 0: otherwise.
    else:
        score = 0
    return score


def reset_coauth_analysis():
    total_coauth_intersections = {}
    total_coauth_intersections["coauth_intersections_full"] = 0
    total_coauth_intersections["coauth_intersections_firstname_lastname"] = 0
    write_to_json(total_coauth_intersections, "results/coauth_analysis.json")
    

def write_to_json(json_val,filepath):
    with open(filepath, "w") as f:
        json.dump(json_val, f)
        
        
def append_to_json(json_val,filepath):
    with open(filepath, "a+") as f:
        json.dump(json_val, f)
        

def add_total_profiles_to_score_files():
    key = "total_profiles"
    x1_m[key] = sum(x1_m.values())
    x1_nm[key] = sum(x1_nm.values())
    x2_m[key] = sum(x2_m.values())
    x2_nm[key] = sum(x2_nm.values())
    xa_m[key] = sum(xa_m.values())
    xa_nm[key] = sum(xa_nm.values())
    x10_m[key] = sum(x10_m.values())
    x10_nm[key] = sum(x10_nm.values())
    
    write_to_json(x1_m,"results/x1_m.json")
    write_to_json(x1_nm,"results/x1_nm.json")
    write_to_json(x2_m,"results/x2_m.json")
    write_to_json(x2_nm,"results/x2_nm.json")
    write_to_json(xa_m,"results/xa_m.json")
    write_to_json(xa_nm,"results/xa_nm.json")
    write_to_json(x10_m,"results/x10_m.json")
    write_to_json(x10_nm,"results/x10_nm.json")


def is_match(match):
    is_match_set = None
    fullname1 = match[rowheadings['fullname1']]
    fullname2 = match[rowheadings['fullname2']]
    coautha = match[rowheadings['authors1']]
    coauthb = match[rowheadings['authors2']]
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')
    
    mesh_terms1 = match[rowheadings['mesh_terms1']].lower()
    mesh_terms2 = match[rowheadings['mesh_terms2']].lower()
    mesh1 = mesh_terms1.split(',')
    mesh2 = mesh_terms2.split(',')
    
    if(mesh1 is not None and mesh2 is not None):
        mesh_intersection = len(list(set(mesh1) & set(mesh2)))
    else:
        mesh_intersection = 0

    coauth_intersection = compute_coauth_intersection(coauth1, coauth2, fullname1, fullname2)
    
    if(coauth_intersection >= 1 and mesh_intersection > 1):
        is_match_set = True
    elif (coauth_intersection ==0 and mesh_intersection==0):
        is_match_set = False
#     print("coauth_intersection: ", coauth_intersection)
#     print("mesh_intersection: ", mesh_intersection)
    return is_match_set
    
            
def load_nicknames():
    # with open('nick_names.txt', 'r') as f:
    #     lines = f.readlines()
    nicknames = {}
    # for line in lines:
    #     split_line = line.split("  ")
    #     try:
    #         if '/' not in split_line:
    #             nicknames[split_line[0].strip().lower()] = [x.strip().lower() for x in split_line[1].split(',')]
    #     except Exception as e:
    #         pass
    # with open('nicknames.json', 'w') as fp:
    #     json.dump(nicknames, fp)
    # print(len(nicknames.keys()))
    with open('nicknames.json','r') as f:
        nicknames = json.load(f)
    return nicknames        


def oneeditdistance(s1,s2):
	# Find lengths of given strings 
	m = len(s1) 
	n = len(s2) 

	# If difference between lengths is more than 1, 
	# then strings can't be at one distance 
	if abs(m - n) > 1: 
		return False 

	count = 0 # Count of isEditDistanceOne 

	i = 0
	j = 0
	while i < m and j < n: 
		# If current characters dont match 
		if s1[i] != s2[j]: 
			if count == 1: 
				return False 

			# If length of one string is 
			# more, then only possible edit 
			# is to remove a character 
			if m > n: 
				i+=1
			elif m < n: 
				j+=1
			else: # If lengths of both strings is same 
				i+=1
				j+=1
			# Increment count of edits 
			count+=1
		else: # if current characters match 
			i+=1
			j+=1
	# if last character is extra in any string 
	if i < m or j < n: 
		count+=1

	return count == 1


def nickname_match(firstname1, firstname2):
    if (firstname1 in nicknames and firstname2 in nicknames[firstname1]) or \
        (firstname2 in nicknames and firstname1 in nicknames[firstname2]):
        return True
    return False


def compute_coauth_intersection(coauth1, coauth2, fullname1, fullname2):
    coauth_intersection = 0
    
#     with open("results/coauth_analysis.json","r") as f:
#         total_coauth_intersections = json.load(f)
    
    coauth1 = [x.replace(".","").lower() for x in coauth1]
    coauth2 = [x.replace(".","").lower() for x in coauth2]
    fullname1 = fullname1.replace(".","").lower()
    fullname2 = fullname2.replace(".","").lower()
    

    for auth1 in coauth1:
        if auth1 in coauth2:
#             total_coauth_intersections["coauth_intersections_full"]+=1
            coauth_intersection+=1
        elif (auth1.split(" ")[0] in [x.split(" ")[0] for x in coauth2] and \
            auth1.split(" ")[len(auth1.split(" "))-1] in [x.split(" ")[len(x.split(" "))-1] for x in coauth2]):
#             total_coauth_intersections["coauth_intersections_firstname_lastname"]+=1
            coauth_intersection+=1
    
#     with open("results/coauth_analysis.json","w") as f:
#         json.dump(total_coauth_intersections,f)
        
    if(fullname1 == fullname2):
        return coauth_intersection-1
    else:
        return coauth_intersection


    
def compute_x10_(match):
    is_match_set = is_match(match)
    compute_x10(match, is_match_set)
    
    
def compute_x10(match, is_match_set):
    if is_match_set is not None:
        print("is match?", is_match_set)
        firstname1 = match[rowheadings['first_name1']]
        firstname2 = match[rowheadings['first_name2']]
        firstname1 = firstname1.replace(".","").lower()
        firstname2 = firstname2.replace(".","").lower()
        print(firstname1)
        print(firstname2)

        score = get_x10_score(firstname1, firstname2)


        if(is_match_set):
            if score not in x10_m:
                x10_m[score] = 0
            x10_m[score]+=1
        else:
            if score not in x10_nm:
                x10_nm[score] = 0
            x10_nm[score]+=1

        with open('results/x10_m.json', 'w') as fp:
            json.dump(x10_m, fp)
        with open('results/x10_nm.json', 'w') as fp:
            json.dump(x10_nm, fp)


def compute_x1(match):
    is_match_set = is_match(match)
    if (is_match_set is not None):
        print("is match?", is_match_set)
        init2a = match[rowheadings['middle_initial1']].lower().replace('.','')
        init2b = match[rowheadings['middle_initial2']].lower().replace('.','')
        print(init2a)
        print(init2b)
        value = get_x1_score(init2a, init2b)

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

        with open('results/x1_m.json', 'w') as fp:
            json.dump(x1_m, fp)
        with open('results/x1_nm.json', 'w') as fp:
            json.dump(x1_nm, fp)


def compute_x2(match):
    is_match_set = is_match(match)
    if is_match_set is not None:
        print("is match?", is_match_set)
        suffa = match[rowheadings['suffix1']].lower().replace('.','')
        suffb = match[rowheadings['suffix2']].lower().replace('.','')

        value = get_x2_score(suffa, suffb)

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

        with open('results/x2_m.json', 'w') as fp:
            json.dump(x2_m, fp)
        with open('results/x2_nm.json', 'w') as fp:
            json.dump(x2_nm, fp)

        
def compute_xa(match, is_match_set= True):
    fullname1 = match[rowheadings['fullname1']].lower()
    fullname2 = match[rowheadings['fullname2']].lower()
    coautha = match[rowheadings['authors1']].lower()
    coauthb = match[rowheadings['authors2']].lower()
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')
    journal_name1 = match[rowheadings['journal_name1']].lower()
    journal_name2 = match[rowheadings['journal_name2']].lower()
    mesh1 = match[rowheadings['mesh_terms1']].lower().split(',')
    mesh2 = match[rowheadings['mesh_terms2']].lower().split(',')
    langa = match[rowheadings['language1']].lower()
    langb = match[rowheadings['language2']].lower()
    title1 = match[rowheadings['title1']].lower()
    title2 = match[rowheadings['title2']].lower()

    
    x3,x4, x5, x6, x7 = get_xa_score(title1, title2, journal_name1, journal_name2, coauth1, coauth2, fullname1, fullname2, mesh1, mesh2, langa, langb)
    
    value = str([x3, x4, x5, x6, x7])
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
    
    if(is_match_set):
        if(x3 in x3_m):
            x3_m[x3] += 1
        else:
            x3_m[x3] = 1
        if(x4 in x4_m):
            x4_m[x4] += 1
        else:
            x4_m[x4] = 1
        if(x5 in x5_m):
            x5_m[x5] += 1
        else:
            x5_m[x5] = 1
        if(x6 in x6_m):
            x6_m[x6] += 1
        else:
            x6_m[x6] = 1
        if(x7 in x7_m):
            x7_m[x7] += 1
        else:
            x7_m[x7] = 1
    else:
        if(x3 in x3_nm):
            x3_nm[x3] += 1
        else:
            x3_nm[x3] = 1
        if(x4 in x4_nm):
            x4_nm[x4] += 1
        else:
            x4_nm[x4] = 1
        if(x5 in x5_nm):
            x5_nm[x5] += 1
        else:
            x5_nm[x5] = 1
        if(x6 in x6_nm):
            x6_nm[x6] += 1
        else:
            x6_nm[x6] = 1
        if(x7 in x7_nm):
            x7_nm[x7] += 1
        else:
            x7_nm[x7] = 1


#todo: mark view row as completed after compute_xa(match)
def compute_xa_allmatches():
    #count = get_article_match_set_pair_count()
    offset = 0
    computed_count = 0
    while(1):
        # article_match_set = sql_client.execute_and_fetch('select * from article_match')
        article_match_set = sql_client.execute_and_fetch('select * from article_match'+
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(article_match_set)

        for match in article_match_set:
            try:
                compute_xa(match, True)
                # mark_as_done(match, 'article_match')
            except Exception as e:
                print(e)
        offset+=limit+1

        if len(article_match_set) == 0:
            break
        print('computed xa_m for ',str(computed_count),' profiles')

    with open('results/xa_m.json', 'w') as fp:
        json.dump(xa_m, fp)
    write_to_json(x3_m,"results/x3_m.json")
    write_to_json(x4_m,"results/x4_m.json")
    write_to_json(x5_m,"results/x5_m.json")
    write_to_json(x6_m,"results/x6_m.json")
    write_to_json(x7_m,"results/x7_m.json")


def compute_xa_allnonmatches():
#     count = get_article_non_match_set_pair_count()
    offset = 0
    computed_count = 0
    
    while(1):
        query = 'select * from article_non_match'
        print(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        article_non_match_set = sql_client.execute_and_fetch(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        computed_count +=len(article_non_match_set)

        for match in article_non_match_set:
            try:
                compute_xa(match, False)
                # mark_as_done(match, 'article_non_match')
            except Exception as e:
                print(e)
        offset+=limit

        if len(article_non_match_set) == 0:
            break
        print('computed xa_nm for ',str(computed_count),' profiles')
        with open('results/xa_nm_'+str(offset)+'.json', 'w') as fp:
            json.dump(xa_nm, fp)
        write_to_json(x3_nm,'results/x3_nm_'+str(offset)+'.json')
        write_to_json(x4_nm,'results/x4_nm_'+str(offset)+'.json')
        write_to_json(x5_nm,'results/x5_nm_'+str(offset)+'.json')
        write_to_json(x6_nm,'results/x6_nm_'+str(offset)+'.json')
        write_to_json(x7_nm,'results/x7_nm_'+str(offset)+'.json')


    with open('results/xa_nm.json', 'w') as fp:
        json.dump(xa_nm, fp)
    write_to_json(x3_nm,'results/x3_nm.json')
    write_to_json(x4_nm,'results/x4_nm.json')
    write_to_json(x5_nm,'results/x5_nm.json')
    write_to_json(x6_nm,'results/x6_nm.json')
    write_to_json(x7_nm,'results/x7_nm.json')
    

def compute_x1_x2_all():
    count = get_name_set_pair_count()
    offset = 0
    computed_count = 0

    while(1):
        name_set = sql_client.execute_and_fetch('select * from name_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(name_set)
        c = 0
        for match in name_set:
            try:
                compute_x1(match)
                compute_x2(match)
                # mark_as_done(match, 'name_set')
            except Exception as e:
                print(e)
        offset+=limit
        if(len(name_set)==0):
            break

        print('computed x1, x2 for ',str(computed_count),' profiles')


def compute_x1_x2_balanced():
    matches_query = "select * from name_matches"
    non_matches_query = "select * from name_non_matches order by random() limit 10000"

    match_set = sql_client.execute_and_fetch(matches_query)
    for match in match_set:
        try:
            x1_value = get_x1_score(match[0], match[1])

            if(x1_value in x1_m):
                x1_m[x1_value] += 1
            else:
                x1_m[x1_value] = 1

            x2_value = get_x2_score(match[2], match[3])

            if(x2_value in x2_m):
                x2_m[x2_value] += 1
            else:
                x2_m[x2_value] = 1
        
            with open('results/x1_m_3k_10k.json', 'w') as fp:
                json.dump(x1_m, fp)
            with open('results/x2_m_3k_10k.json', 'w') as fp:
                json.dump(x2_m, fp)
        except Exception as e:
            print(e)
    
    non_match_set = sql_client.execute_and_fetch(non_matches_query)
    for match in non_match_set:
        try:
            x1_value = get_x1_score(match[0], match[1])

            if(x1_value in x1_nm):
                x1_nm[x1_value] += 1
            else:
                x1_nm[x1_value] = 1
        
            x2_value = get_x2_score(match[2], match[3])

            if(x2_value in x2_nm):
                x2_nm[x2_value] += 1
            else:
                x2_nm[x2_value] = 1
        
            with open('results/x1_nm_3k_10k.json', 'w') as fp:
                json.dump(x1_nm, fp)
            with open('results/x2_nm_3k_10k.json', 'w') as fp:
                json.dump(x2_nm, fp)
        except Exception as e:
            print(e)
       

def store_x1_x2_balanced():
    sql_client.execute("create table IF NOT EXISTS name_matches (init2a VARCHAR(255) NOT NULL, init2b VARCHAR(255) NOT NULL, suffa VARCHAR(255) NOT NULL, suffb VARCHAR(255) NOT NULL)")
    sql_client.execute("create table  IF NOT EXISTS name_non_matches (init2a VARCHAR(255) NOT NULL, init2b VARCHAR(255) NOT NULL, suffa VARCHAR(255) NOT NULL, suffb VARCHAR(255) NOT NULL)")
    count = get_name_set_pair_count()
    offset = 0
    computed_count = 0

    while(1):
        name_set = sql_client.execute_and_fetch('select * from name_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(name_set)
        c = 0
        for match in name_set:
            if(is_match(match)):
                write_to_db("name_matches", match)
            else:
                write_to_db("name_non_matches", match)
        offset+=limit
        if(len(name_set)==0):
            break

def write_to_db(table_name, value):
    init2a = value[rowheadings['middle_initial1']].lower().replace('.','')
    init2b = value[rowheadings['middle_initial2']].lower().replace('.','')
    suffa = value[rowheadings['suffix1']].lower().replace('.','')
    suffb = value[rowheadings['suffix2']].lower().replace('.','')
    sql_client.insert_row("insert into {} (init2a, init2b, suffa, suffb) values (?,?,?,?)".format(table_name), [init2a, init2b, suffa, suffb])


def compute_x10_allmatches():
    count = get_firstname_match_set_pair_count()
    offset = 0
    computed_count = 0

    while(1):
        firstname_match_set = sql_client.execute_and_fetch('select * from name_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(firstname_match_set)
#         print(computed_count," count")
        c = 0
        for match in firstname_match_set:
            try:
                is_match_set = is_match(match)
                if(is_match_set is not None and is_match_set==True):
                    print("is match")
                    compute_x10(match,True)
#                 compute_x2(match)
                # mark_as_done(match, 'name_set')
            except Exception as e:
                print(e)
        offset+=limit
        if(len(firstname_match_set)==0):
            break

        print('computed x10 for ',str(computed_count),' profiles')
        

def compute_x10_allnonmatches():
    count = get_firstname_non_match_set_pair_count()
    offset = 0
    computed_count = 0

    while(1):
        firstname_nonmatch_set = sql_client.execute_and_fetch('select * from firstname_nonmatch_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(firstname_nonmatch_set)
        c = 0
        for match in firstname_nonmatch_set:
            try:
                compute_x10(match, False)
#                 compute_x2(match)
                # mark_as_done(match, 'name_set')
            except Exception as e:
                print(e)
        offset+=limit
        if(len(firstname_nonmatch_set)==0):
            break

        print('computed x10 for ',str(computed_count),' profiles')


def compute_x10_all():
    count = get_name_set_pair_count()
#     count = 10 
    offset = 0
    computed_count = 0

    while(1):
        firstname_nonmatch_set = sql_client.execute_and_fetch('select * from name_set' +
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(firstname_nonmatch_set)
        c = 0
        for match in firstname_nonmatch_set:
            try:
                compute_x10_(match)
#                 compute_x2(match)
                # mark_as_done(match, 'name_set')
            except Exception as e:
                print(e)
        offset+=limit
        if(len(firstname_nonmatch_set)==0):
            break

        print('computed x10 for ',str(computed_count),' profiles')
        


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


def get_firstname_match_set_pair_count():
#     query = 'select count(*) from firstname_match_set'
    query = 'select count(*) from name_set'

    count = sql_client.execute_and_fetch(query)
    print("firstname match set pair count: "+str(count))
    return count


def get_firstname_non_match_set_pair_count():
    query = 'select count(*) from firstname_nonmatch_set'
    count = sql_client.execute_and_fetch(query)
    print("firstname non match set pair count: "+str(count))
    return count
             

def compute_xa_individual_all_matches():
    #count = get_article_match_set_pair_count()
    offset = 0
    computed_count = 0
    while(1):
        # article_match_set = sql_client.execute_and_fetch('select * from article_match')
        article_match_set = sql_client.execute_and_fetch('select * from article_match'+
        ' limit ' + str(limit) + ' offset ' + str(offset))
        computed_count =len(article_match_set)

        for match in article_match_set:
            try:
                compute_xa_individual(match, True)
                # mark_as_done(match, 'article_match')
            except Exception as e:
                print(e)
        offset+=limit+1

        if len(article_match_set) == 0:
            break
        print('computed xa_m for ',str(computed_count),' profiles')

    write_to_json(x3_m,"results/x3_m.json")
    write_to_json(x4_m,"results/x4_m.json")
    write_to_json(x5_m,"results/x5_m.json")
    write_to_json(x6_m,"results/x6_m.json")
    write_to_json(x7_m,"results/x7_m.json")


def compute_xa_individual_all_nonmatches():
#     count = get_article_non_match_set_pair_count()
    offset = 0
    computed_count = 0
    
    while(1):
        query = 'select * from article_non_match'
        print(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        article_non_match_set = sql_client.execute_and_fetch(query + ' limit ' + str(limit) + ' offset ' + str(offset) )
        computed_count +=len(article_non_match_set)

        for match in article_non_match_set:
            try:
                compute_xa_individual(match, False)
                # mark_as_done(match, 'article_non_match')
            except Exception as e:
                print(e)
        offset+=limit

        if len(article_non_match_set) == 0:
            break
        print('computed xa_nm for ',str(computed_count),' profiles')
#         with open('results/xa_nm_'+str(offset)+'.json', 'w') as fp:
#             json.dump(xa_nm, fp)


        write_to_json(x3_nm,'results/x3_nm_'+str(offset)+'.json')
        write_to_json(x4_nm,'results/x4_nm_'+str(offset)+'.json')
        write_to_json(x5_nm,'results/x5_nm_'+str(offset)+'.json')
        write_to_json(x6_nm,'results/x6_nm_'+str(offset)+'.json')
        write_to_json(x7_nm,'results/x7_nm_'+str(offset)+'.json')


sql_client = sqlite_client('../../database/jstor-authority.db')


rowheadings = {}
rowheadings['id1'] = 0
rowheadings['position1'] = 1
rowheadings['last_name1'] = 2
rowheadings['first_initial1'] = 3
rowheadings['middle_initial1'] = 4
rowheadings['suffix1'] = 5
rowheadings['title1'] = 6
rowheadings['journal_name1'] = 7
rowheadings['fullname1'] = 8
rowheadings['first_name1'] = 9
rowheadings['middle_name1'] = 10
rowheadings['language1'] = 11
rowheadings['authors1'] = 12
rowheadings['mesh_terms1'] = 13
rowheadings['affiliation1'] = 14
rowheadings['full_title1'] = 15
rowheadings['id2'] = 16
rowheadings['position2'] = 17
rowheadings['last_name2'] = 18
rowheadings['first_initial2'] = 19
rowheadings['middle_initial2'] = 20
rowheadings['suffix2'] = 21
rowheadings['title2'] = 22
rowheadings['journal_name2'] = 23
rowheadings['fullname2'] = 24
rowheadings['first_name2'] = 25
rowheadings['middle_name2'] = 26
rowheadings['language2'] = 27
rowheadings['authors2'] = 28
rowheadings['mesh_terms2'] = 29
rowheadings['affiliation2'] = 30
rowheadings['full_title2'] = 31


limit = 1000000

x1_m = {}
x1_nm = {}

x2_m = {}
x2_nm = {}

xa_m = {}
xa_nm = {}

x10_m = {}
x10_nm = {}

x3_m = {}
x3_nm = {}

x4_m = {}
x4_nm = {}

x5_m = {}
x5_nm = {}

x6_m = {}
x6_nm = {}

x7_m = {}
x7_nm = {}


nicknames = load_nicknames()
# get_name_set_pair_count()
# get_firstname_match_set_pair_count()
# get_firstname_non_match_set_pair_count()
# get_article_match_set_pair_count()
# get_article_non_match_set_pair_count()



test_pair = ('1305255', 1, 'Erwin', 'D', 'H', '', 'permian gastropoda southwestern united states subulitacea ', 'Journal of Paleontology', 'Douglas H. Erwin', 'Douglas', 'H.', 'eng', 'Douglas H. Erwin', 'Animals,New Mexico,Texas,*Gastropod,Clinical Nursing Research,*Tetraodontiformes,*Nasal Septum', '', 'Permian Gastropoda of the Southwestern United States: Subulitacea', '1305376', 1, 'Erwin', 'D', 'H', '', 'genus glyptospira gastropoda trochacea permian southwestern united states ', 'Journal of Paleontology', 'Douglas H. Erwin', 'Douglas', 'H.', 'eng', 'Douglas H. Erwin', 'Animals,*Phylogeny,Texas,Arizona,New Mexico,Nevada,*Gastropod,*Cingulata,*Limestone,Wounds, Penetrating,Wounds, Nonpenetrating,Southwestern United States,*Bird', '', 'Permian Gastropoda of the Southwestern United States: Subulitacea')
# print(sql_client.execute_and_fetch("select * from name_non_matches"))
# store_x1_x2_balanced()
compute_x1_x2_balanced()


# compute_xa_individual_all_matches()
# compute_xa_individual_all_nonmatches()


# compute_xa_allmatches()
# compute_xa_allnonmatches()
# compute_x10_allmatches()
# compute_x10_allnonmatches()
# reset_coauth_analysis()
# compute_x10_all() 
# compute_x10_(test_pair)

# add_total_profiles_to_score_files()
# print(compute_coauth_intersection(["Saddie Gilbert", "Moody Marshmellow", "F Noname", "Check Case"],["Fu Noname", "M. Marshmellow", "CHECK CASE"],"Love Coder","Hate Coder"))
