
from rich.pretty import pprint
from rich import print
from rich.progress import track
from pathlib import Path
import requests
import gzip

import xmltodict, json

__mesh_files = ['desc2023.gz']

from resolution.database.client import get_client

def run():
    client = get_client('mongo_credentials.json', local=True)
    mesh_collection = client.mesh.mesh

    for mesh_entry in mesh_collection.find():
        pprint(mesh_entry)
