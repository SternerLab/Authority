
from rich.pretty import pprint
from rich import print
import pandas as pd

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    val        = client.validation
    val_types  = val.list_collection_names()
    print(val_types)
    1/0

    names = pd.read_csv('data/names.csv')
    names.sort_values(by='count', ascending=False, inplace=True)

    for tup in names.itertuples():
        print(f'Considering {tup.key}, count {tup.count}')
        missing = False
        total_overlap = 0
        for val_type in val_types:
            col = val[val_type]
            print('Sanity checking validation size', col.count_documents({}))
            overlap = 0
            for match in col.find({'author' : {'key' : tup.key}}):
                overlap += 1
            total_overlap += overlap
            if overlap == 0:
                print(f'No author with key {tup.key} in source {val_type}')
                missing = True
            else:
                print(f'Resolved key {tup.key} in source {val_type} with overlap {overlap}')
        if missing:
            print(f'{tup.key} missing from at least one validation source')
        else:
            print(f'{tup.key} is present in all validation sources, and has count {tup.count} with {total_overlap} total overlapping entries')
