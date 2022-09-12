''' Helper functions for calculating features '''
def _word_intersection(s1, s2):
    return len(set(s1.split(' ')) & set(s2.split(' ')))

def _coauthor_intersection(a, b):
    return 0

import Levenshtein as _lev

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

def _get_mesh(x):
    fetched = x.get('mesh', [])
    if isinstance(fetched, str):
        return []
    else:
        assert isinstance(fetched, list)
        return fetched

def x6(a, b):
    ''' Feature based on words in common between mesh terms '''
    return len(set(_get_mesh(a)) & set(_get_mesh(b)))

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


def x10(a, b):
    clean = lambda s : s.replace(' ', '').replace('-', '')
    a_first = a['first']
    b_first = b['first']
    a_clean = clean(a_first)
    b_clean = clean(b_first)
    hyphen_a = '-' in a_first
    hyphen_b = '-' in b_first
    if hyphen_a:
        a_pre, a_post = a_first.split('-')
    else:
        a_pre = a_first; a_post = ''
    if hyphen_b:
        b_pre, b_post = b_first.split('-')
    else:
        b_pre = b_first; b_post = ''

    if a_first == b_first and len(a_first) > 1:
        # 11: exact match
        return 11
    elif a_clean == b_clean:
        # 10: namewithorwithouthyphen/space(jean-francoisvs.jeanfrancois or jean-
        # francois vs. jean francois),
        return 10
    elif hyphen_a and hyphen_b and a_pre == b_pre and b_post[0] == a_post[0]:
        # 9: hyphenated name vs. name with hyphen and initial (jean-francois vs.
        # jean-f),
        return 9
    elif hyphen_a != hyphen_b and a_pre == b_pre:
        if 1 in {len(a_post), len(b_post)}:
            # 8: hyphenated name with initial vs. name (jean-f vs. jean),
            return 8
        else:
            # 7: hyphenated name vs. first name only (jean-francois vs. jean)
            return 7
    elif nickname_match(a_first, b_first):
        # 6: nickname match (dave vs. david)
        return 6
    elif _lev.distance(a_first, b_first) == 1:
        # 5: oneeditdistance(deletion:bjoernvs.bjorn,replacement:bjoernvs.bjaern,
        # or flip order of two characters: bjoern vs. bjeorn)
        return 5
    elif a_first in b_first or b_first in a_first:
        l_a = len(a_first); l_b = len(b_first)
        if l_a > 2 and l_b > 2:
            # 4: name matches first part of other name and length > 2 (zak vs. zakaria)
            return 4
        if l_a == l_b == 2:
            # 3: name matches first part of other name and length = 2 (th vs. thomas)
            return 3
    elif a_first[0] == b_first[0] and (a['middle_initial'] == b['middle_initial']):
        # This case doesn't make sense, since our first names are parsed as single or hyphenated words only, so we can check "middle" names instead
        return 2
    elif a_first[0] == b_first[0] and len(a_first) == 1 or len(b_first) == 1:
        # 1: same first initial if one of them only has initial given,
        return 1
    else:
        return 0
