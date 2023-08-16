from ..algorithm.inference import *
from dataclasses import dataclass, field
import dill as pickle
import warnings

from ..algorithm.components import connected_components
from ..authority.clustering import cluster as agglomerative_probs
from ..authority.compare    import compare_pair

@dataclass
class Classifier(InferenceMethod):
    lookup_name: str = ''

    def __post_init__(self):
        assert self.lookup_name is not None, f'Must provide a name within baselines collection'
        doc = self.client.baselines.classifiers.find_one({'name' : self.lookup_name})
        try:
            binary = doc.get('binary')
            if binary is None:
                raise RuntimeError(f'No binary found in database for {self.lookup_name}')
            self.classifier = pickle.loads(binary)
            self.cluster_params['method'] = self.hyperparams.get('method', 'components')
        except:
            raise KeyError(f'Could not find classifier with name {self.lookup_name}')

    def pairwise_infer(self, pair, **pairwise_params): # -> cond_prob
        compared = compare_pair(pair)
        features = np.array(list(compared['features'].values())).reshape(1, -1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self.classifier.predict_proba(features)[0, 0]

    def pair_cluster_method(self, table, **cluster_params):
        match cluster_params['method']:
            case 'components':
                labels = connected_components(table)
            case 'agglomerative':
                labels = agglomerative_probs(table)
            case _:
                print(cluster_params)
                raise RuntimeError(f'Must specify method')
        return labels
