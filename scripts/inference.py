from pymongo import MongoClient
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from pathlib import Path

from resolution.authority.inference import *
from resolution.algorithm.inference import *

def run():
    client    = MongoClient('localhost', 27017)

    # authority = AuthorityInferenceMethod(client, name='authority',
    #                                      correct_triplets=True,
    #                                      reestimate=True,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='default'))

    authority = AuthorityInferenceMethod(client, name='authority',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='default'))

    query = {}
    methods = [authority]
    inference(client, methods, query=query)
