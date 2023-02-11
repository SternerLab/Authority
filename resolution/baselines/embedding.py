from ..algorithm.inference import *
from dataclasses import dataclass, field
import dill as pickle
import torch
import hdbscan
import numpy as np
from scipy.spatial import distance

# from rich import print
from rich.pretty import pprint
import logging
log = logging.getLogger('rich')

from ..authority.compare    import compare_pair
from transformers import AutoTokenizer, AutoModelForPreTraining

@dataclass
class EmbeddingClusterer(InferenceMethod):
    direct: bool = field(default=True)
    tokenizer: 'typing.Any' = None
    model: 'typing.Any' = None
    method: str = None

    def __post_init__(self):
        assert self.name is not None, f'Must provide a name'
        assert 'model'  in self.hyperparams, f'Must provide model in hyperparams'
        assert 'method' in self.hyperparams, f'Must provide method in hyperparams'
        model = self.hyperparams['model']
        log.info(f'Loading tokenizer {model}')
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        log.info(f'Loading tokenizer {model}')
        self.model     = AutoModelForPreTraining.from_pretrained(model, output_hidden_states=True)
        self.epsilon   = self.hyperparams['epsilon']

    def infer_direct(self, articles, pair_docs, group_id, group_cache, id_lookup, **kwargs):
        group   = group_cache[str(group_id)]
        doc_ids = [d['ids'] for d in group['group']][:400] # Artificial limit for memory
        ordered_ids  = []
        ordered_vecs = None

        for i, article in enumerate(articles.find({'_id' : {'$in' : doc_ids}})):
            # Not 100% sure about using sep tokens here, it wasn't trained like this
            # But if it were, then we should..
            print(f'{i} / {len(doc_ids)}')
            try:
                description = (article['title'] + self.tokenizer.sep_token +
                               article['journal'] + self.tokenizer.sep_token +
                               article['abstract'])
                inputs      = self.tokenizer.encode_plus(description,
                                                         add_special_tokens=True,
                                                         return_attention_mask=True,
                                                         return_tensors='pt',
                                                         truncation=True,
                                                         padding='max_length',
                                                         max_length=512)
                embedding   = self.model(**inputs)

                vec = np.ravel(embedding['hidden_states'][-1].detach().numpy())
                if ordered_vecs is None:
                    ordered_vecs = np.full((len(doc_ids),) + vec.shape, np.nan)
                ordered_vecs[i, :] = vec
                ordered_ids.append(str(article['_id']))
            except TypeError: # Some corrupted/non uniform articles don't have str abstract/title
                pass

        try:
            if len(doc_ids) < 3 or ordered_vecs is None:
                raise ValueError # Small hack to force merging small clusters
            log.info('Printing example pairwise cosine distances')
            for i, j in itertools.combinations(np.arange(len(doc_ids)), 2):
                print(distance.cosine(ordered_vecs[i, :], ordered_vecs[j, :]))
            clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric=distance.cosine,
                                        allow_single_cluster=True,
                                        # Should learn or at least validate this!
                                        cluster_selection_epsilon=self.epsilon) # Arbitrary :)
            clusterer.fit(ordered_vecs)
            print(clusterer.labels_)
            labels   = dict()
            assigned = dict()
            count    = 0
            for label, mongo_id in zip(clusterer.labels_, ordered_ids):
                if label == -1:
                    labels[mongo_id] = count
                    count += 1
                else:
                    if label in assigned:
                        labels[mongo_id] = assigned[label]
                    else:
                        assigned[label] = count
                        count += 1
            pprint(labels)
            return labels
        except ValueError:
            return {str(mongo_id) : 0 for mongo_id in doc_ids}

    def fill_table(self, pair_docs, group_cache, id_lookup, **pairwise_params):
        raise NotImplementedError # Just in case
