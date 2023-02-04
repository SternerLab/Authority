
import pymongo
from rich.pretty import pprint
from rich.progress import track
from rich import print
from pathlib import Path

from resolution.authority.inference import *
from resolution.algorithm.inference import *
from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=False)

    authority = AuthorityInferenceMethod(client, name='authority',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='torvik'))

    # authority_no_correction = AuthorityInferenceMethod(client, name='authority_no_correction',
    #                                      correct_triplets=False,
    #                                      reestimate=False,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='torvik'))

    # authority_clipped = AuthorityInferenceMethod(client, name='authority_clipped',
    #                                      correct_triplets=True,
    #                                      reestimate=True,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=True,
    #                                          ratios_from='torvik'))

    # authority_mixed = AuthorityInferenceMethod(client, name='authority_mixed',
    #                                      correct_triplets=True,
    #                                      reestimate=True,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='mixed'))

    # authority_self = AuthorityInferenceMethod(client, name='authority_self_citations',
    #                                      correct_triplets=True,
    #                                      reestimate=True,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='self_citations'))

    # authority_no_correction_robust = AuthorityInferenceMethod(client, name='authority_no_correction_robust',
    #                                      correct_triplets=False,
    #                                      reestimate=False,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='torvik_robust'))

    # authority_mixed_no_correction = AuthorityInferenceMethod(client, name='authority_mixed_no_correction',
    #                                      correct_triplets=False,
    #                                      reestimate=False,
    #                                      hyperparams=dict(
    #                                          epsilon=1e-6,
    #                                          clip=False,
    #                                          ratios_from='mixed'))

    authority_legacy_ratios = AuthorityInferenceMethod(client, name='authority_legacy_ratios',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='authority_legacy'))

    authority_torvik_ratios = AuthorityInferenceMethod(client, name='authority_torvik_ratios',
                                         correct_triplets=True,
                                         reestimate=True,
                                         hyperparams=dict(
                                             epsilon=1e-6,
                                             clip=False,
                                             ratios_from='torvik_reported'))

    query = {}
    # query = {'group_id' : {'first_initial' : 'j', 'last': 'smith'}}
    # methods = [authority_clipped, authority_no_correction, authority_mixed, authority_self]
    # methods = [authority_no_correction_robust, authority_mixed_no_correction]
    methods = [authority, authority_legacy_ratios, authority_torvik_ratios]
    inference(client, methods, query=query)
