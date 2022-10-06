from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track, Progress
import rich.prompt
import datetime

def run():
    ''' Rename collections as backups '''
    client = MongoClient('localhost', 27017)

    now = datetime.datetime.now()
    backup_key = f'backup_{now.replace(microsecond=0)}'

    name_prompt = rich.prompt.Prompt('Please provide a backup name, if desired:')
    backup_name = name_prompt.ask()
    if backup_name != '':
        backup_name = '_' + backup_name
    client.r_table.r_table.rename(f'r_table_{backup_key}{backup_name}')
    for ref_key in client.inferred.list_collection_names():
        client.inferred[ref_key].rename(f'{ref_key}_{backup_key}{backup_name}')

