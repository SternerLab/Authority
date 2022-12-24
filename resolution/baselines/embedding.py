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

    def infer_direct(self, articles, pair_docs, group_id, group_cache, id_lookup, **kwargs):
        group   = group_cache[str(group_id)]
        doc_ids = [d['ids'] for d in group['group']]
        ordered_ids  = []
        ordered_vecs = []
        for article in articles.find({'_id' : {'$in' : doc_ids}}):
            # Not 100% sure about using sep tokens here, it wasn't trained like this
            # But if it were, then we should..
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
            print(len(inputs['input_ids']))
            embedding   = self.model(**inputs)
            print(embedding['hidden_states'][-1].shape)
            ordered_vecs.append(np.expand_dims(np.ravel(embedding['hidden_states'][-1].detach().numpy()), 0))
            ordered_ids.append(str(article['_id']))

        ordered_vec_mx = np.concatenate(ordered_vecs, axis=0)
        print(ordered_vec_mx.shape)
        l, w = ordered_vec_mx.shape
        log.info('Printing example pairwise cosine distances')
        for i, j in itertools.combinations(np.arange(l), 2):
            print(distance.cosine(ordered_vec_mx[i, :], ordered_vec_mx[j, :]))
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric=distance.cosine,
                                    allow_single_cluster=True,
                                    # cluster_selection_method='leaf',
                                    cluster_selection_epsilon=0.5)
        clusterer.fit(ordered_vec_mx)
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

    def fill_table(self, pair_docs, group_cache, id_lookup, **pairwise_params):
        raise NotImplementedError # Just in case
