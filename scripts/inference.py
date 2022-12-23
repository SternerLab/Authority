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

    authority_no_correction = AuthorityInferenceMethod(client, name='authority_no_correction',
                                         correct_triplets=False,
                                         reestimate=False,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='torvik'))

    authority_clipped = AuthorityInferenceMethod(client, name='authority_clipped',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=True,
                                             ratios_from='torvik'))

    authority_mixed = AuthorityInferenceMethod(client, name='authority_mixed',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='mixed'))

    authority_self = AuthorityInferenceMethod(client, name='authority_self_citations',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='self_citations'))

    query = {}
    methods = [authority_clipped, authority_no_correction, authority_mixed, authority_self]
    inference(client, methods, query=query)
