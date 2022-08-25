from . import features

feature_dict = {f'x{i}' : getattr(features, f'x{i}') for i in range(1, 8)}

def compare(a, b):
    return {k : f(a, b) for k, f in feature_dict.items()}
