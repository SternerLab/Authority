from ..algorithm.inference import *
from dataclasses import dataclass, field
import dill as pickle

from ..algorithm.components import connected_components
from ..authority.clustering import cluster as agglomerative_probs
from ..authority.compare    import compare_pair

@dataclass
class Cluster(InferenceMethod):
    full: bool = True # If the entire dataset should be used, or just features

    def __post_init__(self):
        assert self.name is not None, f'Must provide a name within baselines collection'
        binary = self.client.baselines.cluster_algorithms.find_one({name : self.name})
        self.cluster_alg = pickle.loads(binary)
        1/0
