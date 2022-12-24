from pymongo import MongoClient
from rich.pretty import pprint


def run():
    print('Checking articles in MongoDB', flush=True)
    client     = MongoClient('localhost', 27017)
    validation = client.validation

    for val_type in validation.list_collection_names():
        coll = validation[val_type]
        if 'orcid' in val_type:
            if 'lookup' in val_type:
                total = 0
                for lookup_table in coll.find():
                    total += len(lookup_table['lookup'])
                print(total)
            else:
                continue
        else:
            total = coll.count_documents({})
        print(f'{val_type}: {total}')
