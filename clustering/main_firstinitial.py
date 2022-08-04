# coding=utf-8
import pandas as pd
import itertools as itertools
import json
import statistics
import random
import clustering as clustering
import sqlite3
import ast
import sys
import time


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
    with open('r_table/nicknames.json','r') as f: #change this todo
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


def compare(str_x, str_y):
    # print("str", str_x, str_y)
    x = json.loads(str_x) #converst string representation of list to list
    y = json.loads(str_y)
    x_less_than_y_count = 0
    x_greater_than_y_count = 0
    for i in range(0, len(x)):
        if(x[i] <= y[i]):
            x_less_than_y_count+=1
        if(x[i] >= y[i]):
            x_greater_than_y_count+=1
    if x_less_than_y_count == len(x):
        return -1
    elif x_greater_than_y_count == len(x):
        return 1
    else:
        return 0
    
    
def create_blocks(cnx, query, group_by_list):
    df = pd.read_sql(query, cnx)
    group_by = df.groupby(group_by_list)
    return group_by
      


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
    firstname1 = match['first_name'][0]
    firstname2 = match['first_name'][1]
    firstname1 = firstname1.replace(".","").lower()
    firstname2 = firstname2.replace(".","").lower()
    score = get_x10_score(firstname1, firstname2)

    if score not in x10:
        x10[score] = 0
    x10[score]+=1
    return score
        
    
def compute_x1(row):
    init2a = row["middle_initial"][0].lower().replace('.','')
    init2b = row["middle_initial"][1].lower().replace('.','')
    value = get_x1_score(init2a, init2b)

    if(value in x1):
        x1[value] += 1
    else:
        x1[value] = 1
    return value



def compute_x2(row):
    suffa = row['suffix'][0].lower()
    suffb = row['suffix'][1].lower()

    value = get_x2_score(suffa, suffb)
    if(value in x2):
        x2[value] += 1
    else:
        x2[value] = 1
    return value


def compute_xa(row):
    fullname1 = row['fullname'][0].lower()
    fullname2 = row['fullname'][1].lower()
    coautha = row['authors'][0].lower()
    coauthb = row['authors'][1].lower()
    coauth1 = coautha.split(',')
    coauth2 = coauthb.split(',')
    title1 = row['title'][0].lower()
    title2 = row['title'][1].lower() 
    langa = row['language'][0].lower()
    langb = row['language'][1].lower()
    mesh1 = row['mesh_terms'][0].lower()
    mesh2 = row['mesh_terms'][1].lower()
    journal_name1 = row['journal_name'][0].lower()
    journal_name2 = row['journal_name'][1].lower()
    coauth_intersection = compute_coauth_intersection(coauth1, coauth2, fullname1, fullname2)

    x3, x4, x5, x6, x7 = get_xa_score(title1, title2, journal_name1, journal_name2, coauth1, coauth2, fullname1, fullname2, mesh1, mesh2, langa, langb)
    value = str([x3, x4, x5, x6, x7])
    if(value in xa):
        xa[value] += 1
    else:
        xa[value] = 1
    return value


def lookup(input):
    key1 = str(input[0])
    key2 = str(input[1])
    keya = str(input[2])
    key10 = str(input[3])
    value = None
    
    if(key1 in r_x1 and key2 in r_x2 and keya in r_xa and key10 in r_x10):
        value= r_x1[key1]*r_x2[key2]*r_xa[keya]*r_x10[key10]
    else:
        value= r_x1[key1]*r_x2[key2]*extrapolate(input[2])*r_x10[key10]
#     with open("results/score_analysis.txt",'a+') as f:
#         f.write(key1+","+key2+","+keya+","+key10+" : "+str(value)+"\n")
    return value


def get_difference(key1, key2):
    x = json.loads(key1) #converst string representation of list to list
    y = json.loads(key2)
    diff = 0
    for i in range(0, len(x)):
        diff += abs(x[i] - y[i])
    return diff


def get_upper_profile_key():
    upper_profiles = ''
    with open('r_table/upper_profiles.txt', 'r') as f:
        upper_profiles = f.readlines()
    upper_profiles = ast.literal_eval(upper_profiles[0])

#     print(upper_profiles)
    x3_max, x4_max, x5_max, x6_max, x7_max = 0,0,0,0,0
    for profile in upper_profiles:
        profile_attributes = json.loads(profile)
        x3_max, x4_max, x5_max, x6_max, x7_max = max(x3_max, profile_attributes[0]), max(x4_max, profile_attributes[1]), max(x5_max, profile_attributes[2]), max(x6_max, profile_attributes[3]), max(x7_max, profile_attributes[4])
    return [x3_max, x4_max, x5_max, x6_max, x7_max]


def extrapolate(key):
#     xnew  (min{9, x3}, min{1, x4}, min{7, x5}, min{9, x6},
# min{12, x8}, min{1, x9}),
    x_new = []
#     upper_profiles = ['[9, 0, 0, 10]', '[6, 1, 0, 15]', '[9, 1, 0, 8]', '[11, 1, 0, 6]', '[8, 1, 0, 9]', '[7, 1, 
# 0, 12]', '[10, 1, 0, 7]', '[14, 1, 0, 5]']
    key = json.loads(key)
    upper_profile_key = get_upper_profile_key()
    x_new.append(min(upper_profile_key[0], key[0]))
    x_new.append(min(upper_profile_key[1], key[1]))
    x_new.append(min(upper_profile_key[2], key[2]))
    x_new.append(min(upper_profile_key[3], key[3]))
    x_new.append(min(upper_profile_key[4], key[4]))

    
    # print(str(x_new)," extrapolated key ", str(key))
    if str(x_new) in r_xa:
        return r_xa[str(x_new)]
    else:
        # print("extrapolated key not found", str(x_new))
        # # print(str(x_new))
        # return random.uniform(0, 1)
# def get_preceeding_profile(key, _list):
        min_dist = 100
        min_key = -1
        _list = list(r_xa.keys())
        for i in range(0, len(_list)):
            if compare(str(key),_list[i]) > 0:
                diff = get_difference(str(key), _list[i])
                if diff < min_dist:
                    # print(key,_list[i],diff)
                    min_key = _list[i]
#         print("str(min_key)", str(key))
        return r_xa[str(min_key)]


def probability(r, pm):
    return 1/(1+ ((1-pm)/(pm*r)))


def get_pij_pjk_pik(value, prob):
    i = value[1]["id"][0]
    j = value[1]["id"][1]
    k = value[1]["id"][2]
    last_name = value[1]["last_name"][0]
#     first_initial = value[1]["first_name"][0]
    first_initial = value[1]["first_initial"][0]
    key_ij = str([i,j, last_name, first_initial])
    key_jk = str([j,k, last_name, first_initial])
    key_ik = str([i,k, last_name, first_initial])
    p_ij = prob[key_ij]
    p_jk = prob[key_jk]
    p_ik = prob[key_ik]
    keys_arr = [key_ij,key_jk,key_ik]
    prob_arr = [p_ij,p_jk,p_ik]
    return zip(*sorted(zip(prob_arr, keys_arr), reverse=True))


def add_to_prob_dict(key, value, dictionary):
    if key in dictionary:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]


def is_violated(value, prob):
    probabilities, keys = get_pij_pjk_pik(value, prob)
    if probabilities[0] + probabilities[1] - 1 > probabilities[2] + 0.05:
        return True
    return False


def triplet_corrections(prob, df_group):
    df_triplets = df_group.apply(lambda x: list(itertools.combinations(x, 3)), result_type='expand')
    new_prob = {}
    iterations = 0
    violations = 1

    #todo: check keys reverse order existence
    while iterations<30 and violations>0:
        violations = 0
        new_prob = {}

        for value in df_triplets.iterrows():
            try:
                if is_violated(value, prob):
                    # print("isviolated")
                    violations += 1
                    probabilities, keys = get_pij_pjk_pik(value, prob)
                    p_ij = probabilities[0]
                    p_jk = probabilities[1]
                    p_ik = probabilities[2]
                    
                    w_ij = 1 / (p_ij * (1-p_ij))
                    w_jk = 1 / (p_jk * (1-p_jk))
                    w_ik = 1 / (p_ik * (1-p_ik))
                    den = w_ij*w_ik + w_ik*w_jk + w_ij*w_jk

                    q_ij = (w_ij*(w_jk + w_ik)*p_ij + w_jk*w_ik*(1 + p_ik - p_jk))/den
                    q_jk = (w_jk*(w_ij + w_ik)*p_jk + w_ij*w_ik*(1 + p_ik - p_ij))/den
                    q_ik = q_ij + q_jk - 1

                    key_ij = keys[0]
                    key_jk = keys[1]
                    key_ik = keys[2]

                    add_to_prob_dict(key_ij, q_ij, new_prob)
                    add_to_prob_dict(key_ik, q_ik, new_prob)
                    add_to_prob_dict(key_jk, q_jk, new_prob)
            except Exception as e:
                print(str(e))
        
        for key in new_prob.keys():
            adj_edges = new_prob[key]
            prob[key] = sum(adj_edges) / float(len(adj_edges))

        if violations == 0:
            break
        
        with open('results/updated_prob_triplet_'+index_from+'_'+index_to+'.json', 'w') as f:
            json.dump(prob, f)
        iterations+=1

    return prob


def updated_prior(prob):
    keys = [key for key, values in prob.items() if values >= 0.5]
    return len(keys) / float(len(prob.items())+1)


def pairwise_probability_compute(pm, prob, df_group):
    author_key = None
    
    try:
        df = df_group.apply(lambda x: list(itertools.combinations(x, 2)), result_type='expand')
        count = 0
        total_count = 0
        for row in df.iterrows():
            total_count += 1
            _x1 = (compute_x1(row[1]))
            _x2 = (compute_x2(row[1]))
            _xa = (compute_xa(row[1]))
            _x10 = (compute_x10_(row[1]))
            x = [_x1, _x2, _xa, _x10]
#             with open("results/score_analysis.txt",'a+') as f:
#                 f.write(str(row[1]))
            r_value = lookup(x)
            key = str([row[1]["id"][0], row[1]["id"][1], row[1]["last_name"][0], row[1]["first_initial"][0]])
            author_key = row[1]["fullname"][0]
            # print(x)
            if r_value is not None:
                if key not in prob:
                    prob[key] = probability(r_value,pm)
            else:
                count +=1
                if key not in prob:
                    prob[key] = random.uniform(0, 1)

        with open('results/prob_before_triplet_'+index_from+'_'+index_to+'.json', 'w') as f:
            json.dump(prob, f)
    except Exception as e:
        print("exception ",str(e))
    
    # print(count)
    # print(total_count)
    return prob, author_key


def insert_cluster_records(first_initial_last_name, total_records,clusters, total_clusters, authors, authors_count):
    query = "INSERT INTO clusters (first_initial_last_name, total_records, clusters, total_clusters, authors, author_count) VALUES (?, ?, ?, ?, ?, ?)"
    values = first_initial_last_name, total_records,clusters, total_clusters, authors, authors_count
    try:
        cursor.execute(query, values)
        cnx.commit()
    except Exception as e:
        print("Exception while inserting cluster")
        print(str(e))
        if('Duplicate entry' in str(e)):
            print(str(e))
            print(file)
        else:
            with open('results/clusters_exception_'+index_from+'_'+index_to+'.txt', 'a+') as f:
                f.write(first_initial_last_name+":"+str(total_records)+":"+clusters+":"+str(total_clusters)+":"+authors+":"+str(authors_count))
                f.write('\n')
#             sleep(20)
            print("")
        

import os
if not os.path.exists('results'):
    os.makedirs('results')

cnx = sqlite3.connect('../database/jstor-authority.db')
cursor = cnx.cursor()


query = 'SELECT * FROM articles'
group_by_list = ['last_name', 'first_initial']
block_groups = create_blocks(cnx, query, group_by_list)

distinct_names_query = 'SELECT distinct last_name, first_initial FROM articles'
cursor.execute(distinct_names_query)
names = list(cursor.fetchall())
print(len(names))

x1 = {}
x2 = {}
xa = {}
x10 = {}

with open('r_table/r_x1.json') as json_file: 
    r_x1 = json.load(json_file) 
with open('r_table/r_x2.json') as json_file: 
    r_x2 = json.load(json_file) 
with open('r_table/r_final.json') as json_file: 
    r_xa = json.load(json_file) 
with open('r_table/r_x10.json') as json_file: 
    r_x10 = json.load(json_file)

# prob = {}
nicknames = load_nicknames()
cluster_json = {}
# print(type(block_groups))

index_from = sys.argv[1]
index_to = sys.argv[2]
total = 0

# for group_name, df_group in block_groups:
for group_name in names[int(index_from):int(index_to)]:
    prob = {}
    try:
        df_group = block_groups.get_group(group_name)
        print(group_name[0]+' '+group_name[1])
        with open('results/cluster_authors'+index_from+'_'+index_to+'.txt', 'a+') as f:
            f.write(group_name[0]+' '+group_name[1])
            f.write('\n')
        n = df_group.shape[0]
        authors_list = ','.join(set(x.lower().strip().replace('  ',' ') for x in df_group['fullname'].to_list()))
        authors_count = len(authors_list)
        total+=1
    except Exception as e:
        print(e)
    if n > 1:
        try:
            pm = 1/ (1+(10**-1.194)*(n**0.7975))
            
            initial_prob, auth_key = pairwise_probability_compute(pm, prob, df_group)

            pm = updated_prior(initial_prob)
            
            prob, auth_key = pairwise_probability_compute(pm, initial_prob, df_group)
            
            triplet_prob = triplet_corrections(prob, df_group)
            
            pm = updated_prior(triplet_prob)
            prob, auth_key = pairwise_probability_compute(pm, triplet_prob, df_group)
            final_prob = triplet_corrections(prob, df_group)
            clusters = clustering.get_clusters(final_prob, group_name[0], group_name[1])
            cluster_json[group_name[0]+'_'+group_name[1]+'_'+str(n)] = len(clusters)
                

            with open('results/clusters_all_'+index_from+'_'+index_to+'.txt', 'a+') as cluster_file:
                print("file")
                cluster_file.write(group_name[0]+'_'+group_name[1]+':'+str(n)+":" \
                                   +str(clusters)+":"+str(len(clusters))+":"+authors_list)

                cluster_file.write('\n')
        except Exception as e:
            print(e)


with open('results/x1.json', 'w') as f:
    json.dump(x1, f)

with open('results/x2.json', 'w') as f:
    json.dump(x2, f)

with open('results/xa.json', 'w') as f:
    json.dump(xa, f)

with open('results/x10.json', 'w') as f:
    json.dump(x10, f)
cnx.close()