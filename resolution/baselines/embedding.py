from ..algorithm.inference import *
from dataclasses import dataclass, field
import dill as pickle

from rich import print
from rich.pretty import pprint
import logging
log = logging.getLogger('rich')

from ..authority.compare    import compare_pair
from transformers import AutoTokenizer, AutoModel

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
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model     = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')

    def infer_direct(self, pair_docs, group, id_lookup, **kwargs):
        print(pair_docs)
        print(group)
        print(id_lookup)
        1/0

    def fill_table(self, pair_docs, group, id_lookup, **pairwise_params):
        raise NotImplementedError # Just in case
