from rich.pretty import pprint

from . import (
    parse,
    mesh,
    subset,
    sample_pairs,
    features,
    ratio_table,
    inference,
    baselines
    naive_bayes_baseline
    xgboost_baseline
    validate
    )

from resolution.database.client import get_client

def run():
    print('Running end-to-end author resolution', flush=True)
    client = get_client('mongo_credentials.json', local=False)
    # Run the whole resolution authority in one go!
    # Good luck!
    parse.run()
    mesh_from_txt.run()
    subset.run()
    sample_pairs.run()
    features.run()
    ratio_table.run()
    inference.run()
    naive_bayes_baseline.run()
    xgboost_baseline.run()
    baselines.run()
    validate.run()
