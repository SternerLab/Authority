from . import features as _features
from rich.pretty import pprint

feature_dict = {f'x{i}' : getattr(_features, f'x{i}') for i in range(1, 11)}

def compare(a, b):
    return {k : f(a, b) for k, f in feature_dict.items()}

x_a = [3, 4, 5, 6]
limits  = dict(x3=9, x4=1, x5=9, x6=9) # Updated
excluded_features = {8, 9}
x_i = [i for i in range(1, 11) if i not in x_a and i not in excluded_features]

def compare_pair(pair):
    a, b = pair['pair']
    feature_dict = compare(a, b)
    for k, l in limits.items():
        feature_dict[k] = min(feature_dict[k], l)
    return dict(pair=[a, b], features=feature_dict)
