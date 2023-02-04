from rich.pretty import pprint

from . import (
    parse,
    subset,
    sample_pairs,
    features,
    ratio_table,
    inference,
    validate
    )

from resolution.database.client import get_client

def run():
    print('Running end-to-end author resolution', flush=True)
    client = get_client('mongo_credentials.json', local=False)
    # Run the whole resolution authority in one go!
    # parse.run()
    subset.run()
    sample_pairs.run()
    features.run()
    ratio_table.run()
    inference.run()
    validate.run()
