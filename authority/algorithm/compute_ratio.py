from rich.pretty import pprint
from rich import print
import scipy
import numpy as np
from collections import OrderedDict
import warnings

from .compare import *

class IncompleteRatioTable(Warning):
    pass

def get_count(group, feature):
    result = group.find_one({'_id' : feature})
    if result is None:
        return 0
    else:
        return result['count']

def compute_ratio(feature, feature_groups, # match_count, non_match_count,
                  total_matches, total_non_matches, suffix=''):
    ''' Compute r and w:
            key: feature as a tuple
            r: (match prob : non match prob) ratio
            w: total count of feature '''

    match_group     = feature_groups[f'soft_match' + suffix]
    non_match_group = feature_groups[f'differing_last_name' + suffix]

    print('match_group', match_group.count_documents({}))
    print('non_match_group', non_match_group.count_documents({}))

    match_count     = get_count(match_group, feature)
    non_match_count = get_count(non_match_group, feature)
    try:
        r = (match_count / total_matches) / (non_match_count / total_non_matches)
        assert r >= 0., f'ratios should ALWAYS be positive, but got {r} from {match_count} / {total_matches} matches and {non_match_count} / {total_non_matches} non matches'
    except ZeroDivisionError:
        print('Undefined ratio for: ', feature)
        print(f'match count: {match_count} / {total_matches}')
        print(f'non-match count: {non_match_count} / {total_non_matches}')
        r = 0.
    key = tuple(feature.values())
    return key, r, match_count + non_match_count

def compute_xi_ratios(features, feature_groups, x_i):
    ''' Compute ratio of match and non-match frequencies '''
    computed_xi = dict()
    for i in x_i:
        key = f'x{i}'
        ratios = compute_ratios(features, feature_groups, suffix=f'_{key}', xs=[i])
        for value, (r, w) in ratios.items():
            assert r >= 0., f'ratios should ALWAYS be positive, but got {r}'
            computed_xi[(key, value)] = r
    return computed_xi

def compute_ratios(features, feature_groups, suffix='', xs=None):
    ''' Compute ratio of match and non-match frequencies '''
    if xs is None:
        xs = x_a
    total_matches     = features['soft_match'].count_documents(filter={})
    total_non_matches = features['differing_last_name'].count_documents(filter={})

    unique_features = OrderedDict()
    for ref_key in features.list_collection_names():
        print(ref_key + suffix)
        for group in feature_groups[ref_key + suffix].find():
            # Replace None features with 0 here. Should happen earlier, but...
            feature = group['_id']
            key = tuple(el if el is not None else 0 for el in feature.values())
            pprint(group)
            unique_features[key] = feature
            # group['count']
    print('unique_features')
    pprint(unique_features)
    sorted_features = [{f'x{i}' : f for i, f in zip(xs, fs)}
                       for fs in sorted(unique_features.keys())]

    print('sorted features:')
    pprint(sorted_features)

    computed_features = OrderedDict()
    for i, feature in enumerate(sorted_features):
        try:
            key, r, w = compute_ratio(feature, feature_groups,
                                      total_matches,
                                      total_non_matches, suffix=suffix)
            assert r >= 0., f'ratios should ALWAYS be positive, but got {r}'
            computed_features[key] = r, w
        except ZeroDivisionError:
            print('undefined!', i, feature)
            computed_features[key] = 0., 0
    if not computed_features:
        warnings.warn('Ratio table is incomplete, consider regenerating features', IncompleteRatioTable, stacklevel=2)
    return computed_features
