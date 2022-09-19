from rich.pretty import pprint
from rich import print
import scipy
import numpy as np
from collections import OrderedDict

from .compare import *

def get_count(group, feature):
    result = group.find_one({'_id' : feature})
    if result is None:
        return 0
    else:
        return result['count']

def compute_ratio(feature, feature_groups, total_matches, total_non_matches):
    ''' Compute r and w:
            key: feature as a tuple
            r: (match prob : non match prob) ratio
            w: total count of feature '''

    match_group     = feature_groups[f'match']
    non_match_group = feature_groups[f'non_match']

    match_count     = get_count(match_group, feature)
    non_match_count = get_count(non_match_group, feature)
    r = (match_count / total_matches) / (non_match_count / total_non_matches)
    key = tuple(feature.values())
    return key, r, match_count + non_match_count

def compute_ratios(features, feature_groups):
    ''' Compute r scores by comparing match and non-match frequencies '''
    total_matches     = features['match'].count_documents(filter={})
    total_non_matches = features['non_match'].count_documents(filter={})

    unique_features = []
    for ref_key in features.list_collection_names():
        for group in feature_groups[ref_key].find():
            key = tuple(group['_id'].values())
            unique_features.append(key)
    sorted_features = [{f'x{i}' : f for i, f in zip(x_a, fs)}
                       for fs in sorted(unique_features)]

    computed_features = OrderedDict()
    for i, feature in enumerate(sorted_features):
        try:
            key, r, w = compute_ratio(feature, feature_groups,
                                      total_matches,
                                      total_non_matches)
            computed_features[key] = r, w
        except ZeroDivisionError:
            pass
    return computed_features
