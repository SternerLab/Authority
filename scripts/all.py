from rich.pretty import pprint

from . import (
    parse_jstor_articles_from_xml_zip,
    create_mesh_from_fast_text,
    authority_subset,
    authority_sample_pairs,
    authority_features,
    authority_ratio_table,
    authority_inference,
    baselines
    naive_bayes_baseline
    xgboost_baseline
    validate
    )

from resolution.database.client import get_client

def run():
    print('Running end-to-end author resolution', flush=True)
    client = get_client('mongo_credentials.json', local=True)
    print(f'All script is not well-validated and is currently disabled!')
    1/0
    # Run the whole resolution authority in one go!
    # Good luck!
    parse_jstor_articles_from_xml_zip.run()
    create_mesh_from_fast_text()
    authority_subset()
    authority_sample_pairs()
    authority_features()
    authority_ratio_table()
    authority_inference()
    baseline()
    train_naive_bayes_baselin()
    train_xgboost_baselin()
    validate()
