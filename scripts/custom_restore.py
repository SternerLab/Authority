from pymongo import MongoClient
from rich.pretty import pprint
from rich.progress import track, Progress
import rich.prompt
import datetime
import pymongo

def run():
    ''' Rename collections as backups '''
    client = MongoClient('localhost', 27017)
    inf = client.inferred
    inf['first_initial_last_name'].rename('first_initial_last_name_old')
    inf['first_initial_last_name_auto'].rename('first_initial_last_name')
    # inf['first_initial_last_name'].rename('first_initial_last_name_auto')
    # inf['first_initial_last_name_backup_2022-11-02 22:33:19_rerun_nov1'].rename('first_initial_last_name')
