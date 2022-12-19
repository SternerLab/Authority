from ..algorithm.inference import *
from dataclasses import dataclass, field
import dill as pickle

from ..authority.compare    import compare_pair

@dataclass
class Embed(InferenceMethod):
    def __post_init__(self):
        assert self.name is not None, f'Must provide a name within baselines collection'
        self.cluster_alg = pickle.loads(binary)
        1/0
