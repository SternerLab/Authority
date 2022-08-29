''' Helper functions for calculating features '''
def _word_intersection(s1, s2):
    return len(set(s1.split(' ')) & set(s2.split(' ')))

def _coauthor_intersection(a, b):
    return 0

''' Features as individual functions '''
def x1(a, b):
    ''' Feature based on middle initials of each author '''
    match a['middle_initial'], b['middle_initial']:
        case '', '':
            return 2
        case _, '':
            return 1
        case '', _:
            return 1
        case mi_a, mi_b:
            if mi_a == mi_b:
                return 3
            else:
                return 0

def x2(a, b):
    ''' Feature based on the suffixes of each author '''
    sx_a, sx_b = a['suffix'], b['suffix']
    if sx_a != '' and sx_a == sx_b:
        return 1
    else:
        return 0

def x3(a, b):
    ''' Feature based on words in common between titles '''
    return _word_intersection(a['title'], b['title'])

def x4(a, b):
    ''' Feature based on journal title '''
    return 1 if a['journal'] == b['journal'] else 0

def x5(a, b):
    ''' Feature based on intersection between coauthors '''
    keys_a = {auth['key'] for auth in a['authors']}
    keys_b = {auth['key'] for auth in b['authors']}
    return len(keys_a & keys_b) # Technically intersection between authors

def x6(a, b):
    ''' Feature based on words in common between mesh terms '''
    return _word_intersection(a['mesh'], b['mesh'])

def x7(a, b):
    ''' Feature based on common languages, favoring a non-english language match '''
    la = set(a['language'])
    lb = set(b['language'])
    both   = la & lb
    either = la | lb
    non_english = {l for l in either if l != 'eng'}

    for l in non_english:
        if l in both:
            return 3
    if 'eng' in both:
        return 2
    if 'eng' in either:
        return 1
    return 0

def x8(a, b):
    ''' Feature based on words in common between affiliation.
        Will always be 0 for JSTOR since it lacks affiliation data '''
    return _word_intersection(a['affiliation'], b['affiliation'])

def x9(a, b):
    ''' Feature based on empty affiliation, will always be zero '''
    aff_a = set(a['affiliation'].split(' '))
    aff_b = set(b['affiliation'].split(' '))
    return 1 if (not aff_a or not aff_b) else 0


# Reference only
# def get_x10_score(firstname1, firstname2):
#     score = 0
#     hyphen='-'
#     firstname1_withoutspace_hyphen = firstname1.replace(" ","")
#     firstname1_withoutspace_hyphen = firstname1_withoutspace_hyphen.replace(hyphen,"")
#     firstname2_withoutspace_hyphen = firstname2.replace(" ","")
#     firstname2_withoutspace_hyphen = firstname2_withoutspace_hyphen.replace(hyphen,"")
#
#     # 11: exact match,
#     if(firstname1 == firstname2 and len(firstname1) > 1):
#         score = 11
#
#     # 10: namewithorwithouthyphen/space(jean-francoisvs.jeanfrancois or jean-
#     # francois vs. jean francois),
#     elif(firstname1_withoutspace_hyphen == firstname2_withoutspace_hyphen):
#         score = 10
#
#     # 9: hyphenated name vs. name with hyphen and initial (jean-francois vs.
#     # jean-f),
#     elif(hyphen in firstname1 and hyphen in firstname2):
#         if(len(firstname1.split(hyphen)[1]) or len(firstname2.split(hyphen)[1])):
#             if (firstname1.split(hyphen)[1][0] == firstname2.split(hyphen)[1][0]):
#                 score = 9
#     # 8: hyphenated name with initial vs. name (jean-f vs. jean),
#     elif((hyphen in firstname1 and len(firstname1.split(hyphen)[1])==1) or (hyphen in firstname2 and len(firstname2.split(hyphen)[1])==1)):
#         if (firstname1.split(hyphen)[0] == firstname2.split(hyphen)[0]):
#             score = 8
#     # 7: hyphenated name vs. first name only (jean-francois vs. jean)
#     elif(hyphen in firstname1 or hyphen in firstname2):
#         if (firstname1.split(hyphen)[0] == firstname2.split(hyphen)[0]):
#             score = 7
#     # 6: nickname match (dave vs. david)
#     elif nickname_match(firstname1, firstname2):
#         score = 6
#     # 5: oneeditdistance(deletion:bjoernvs.bjorn,replacement:bjoernvs.bjaern,
#     # or flip order of two characters: bjoern vs. bjeorn)
#     elif oneeditdistance(firstname1,firstname2):
#         score = 5
#     # 4: name matches first part of other name and length > 2 (zak vs. zakaria)
#     elif (len(firstname1)>2 and len(firstname2)>2 and (firstname1 in firstname2 or firstname2 in firstname1)):
#         score = 4
#     # 3: name matches first part of other name and length = 2 (th vs. thomas)
#     elif ((len(firstname1)==2 or len(firstname2)==2) and (firstname1 in firstname2 or firstname2 in firstname1)):
#         score = 3
#     # 2: 3-letter initials match (e.g., jean francois g vs. jfg)
#     elif (firstname1==''.join([_name[0] for _name in firstname2.split(' ')]) or firstname2==''.join([_name[0] for _name in firstname1.split(' ')])):
#         score = 2
#     # 1: same first initial if one of them only has initial given,
#     elif (firstname1[0] == firstname2[0] and (len(firstname1) == 1 or len(firstname2) == 1)):
#         score = 1
#     # 0: otherwise.
#     else:
#         score = 0
#     return score
