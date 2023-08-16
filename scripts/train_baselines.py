
from pathlib import Path

import sklearn
import pandas as pd
import numpy  as np

from resolution.baselines.utils import *
from resolution.database.client import get_client

from sklearn.naive_bayes import CategoricalNB
from xgboost import XGBClassifier


def run():
    client = get_client('mongo_credentials.json', local=True)
    np.random.seed(2022)

    models = dict(xgboost=XGBClassifier,
                  naive_bayes=CategoricalNB)

    self_cites = Path('/workspace/JSTOR_self_citations_pairwise.csv.gz')
    heuristic  = Path('/workspace/JSTOR_pairwise.csv.gz')

    self_cites = load_shuffle(self_cites)
    heuristic  = load_shuffle(heuristic)

    for variant, dataset in [('self_citations', self_cites),
                             ('authority_heuristics', heuristic),
                             ('both', pd.concat((self_cites, heuristic)))]:

        for model_name, model_constructor in models.items():
            train_classifier(client, model_constructor, f'{model_name}_{variant}', dataset)

            by_class = dataset.groupby('label')
            balanced = pd.DataFrame(by_class.apply(lambda x: x.sample(by_class.size().min()).reset_index(drop=True)))

            train_classifier(client, model_constructor, f'{model_name}_{variant}_balanced', balanced)

            # filtered = heuristic[heuristic['label'] == True]
            # filtered = pd.concat((filtered, self_cites))
            # train_classifier(client, CategoricalNB, f'{model_name}_{variant}_filtered', filtered)


