''' Helper functions for calculating features '''
def _word_intersection(s1, s2):
    return len(set(s1.split(' ')) & set(s2.split(' ')))

def _coauthor_intersection(a, b):
    return 0

# Just do this globally, pretty painless
import json as _json
with open('resolution/authority/nicknames.json', 'r') as _infile:
    _nicknames = {k : set(v) for k, v in _json.load(_infile).items()}

def _nickname_match(a, b):
    return b in _nicknames.get(a, {}) or a in _nicknames.get(b, {})

import Levenshtein as _lev

''' Features as individual functions '''
def x1(a, b):
    ''' Feature based on middle initials of each author '''
    match a['authors']['middle_initial'], b['authors']['middle_initial']:
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
    sx_a, sx_b = a['authors']['suffix'], b['authors']['suffix']
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
    keys_a = {auth['key'] for auth in a['coauthors']}
    keys_b = {auth['key'] for auth in b['coauthors']}
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

_lang_mappings = {
        'EN' : 'eng',
        }
def x7(a, b, set_based=False):
    ''' Feature based on common languages, favoring a non-english language match '''
    la = {_lang_mappings.get(l, l) for l in a['language']}
    lb = {_lang_mappings.get(l, l) for l in b['language']}

    # This is the version of x7 as it appeared in Torvik originally
    if set_based:
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
    else: # This is our experimental version of x7 that tracks bilingual articles
        la_bi = '-'.join(sorted(la))
        lb_bi = '-'.join(sorted(lb))
        if la_bi == lb_bi and la_bi != 'eng':
            return 3
        elif la_bi == lb_bi and la_bi == 'eng':
            return 2
        elif la_bi != lb_bi:
            if la_bi == 'eng' or lb_bi == 'eng':
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
    a_first = a['authors']['first']
    b_first = b['authors']['first']
    a_clean = clean(a_first)
    b_clean = clean(b_first)
    hyphen_a = '-' in a_first
    hyphen_b = '-' in b_first
    if hyphen_a:
        a_pre, *a_post = a_first.split('-')
        a_post = ''.join(a_post)
    else:
        a_pre = a_first; a_post = ''
    if hyphen_b:
        b_pre, *b_post = b_first.split('-')
        b_post = ''.join(b_post)
    else:
        b_pre = b_first; b_post = ''

    if a_first == '' or b_first == '':
        return 0

    merge_6_to_10 = True

    if a_first == b_first and len(a_first) > 1:
        # 11: exact match
        if merge_6_to_10:
            return 6 # unswapped
        else:
            return 11 # unswapped
    elif not merge_6_to_10 and a_clean == b_clean:
        # 10: namewithorwithouthyphen/space(jean-francoisvs.jeanfrancois or jean-
        # francois vs. jean francois),
        return 10 # unswapped
    elif not merge_6_to_10 and (hyphen_a and hyphen_b and a_pre == b_pre and
          len(a_post) > 0 and len(b_post) > 0 and b_post[0] == a_post[0]):
        # 9: hyphenated name vs. name with hyphen and initial (jean-francois vs.
        # jean-f),
        return 9
    elif not merge_6_to_10 and hyphen_a != hyphen_b and a_pre == b_pre:
        if 1 in {len(a_post), len(b_post)}:
            # 8: hyphenated name with initial vs. name (jean-f vs. jean),
            return 8
        else:
            # 7: hyphenated name vs. first name only (jean-francois vs. jean)
            return 7
    elif not merge_6_to_10 and _nickname_match(a_first, b_first):
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
        try:
            if a_first[0] == b_first[0] and (a['authors']['middle_initial'] == b['authors']['middle_initial']):
                # This case doesn't make sense, since our first names are parsed as single or hyphenated words only, so we can check "middle" names instead
                return 2
            if a_first[0] == b_first[0] and len(a_first) == 1 or len(b_first) == 1:
                # 1: same first initial if one of them only has initial given,
                return 1
        except IndexError:
            return 0
    return 0 # This is a catch all that triggers for empty names and other edge cases
