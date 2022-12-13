from pymongo import MongoClient
# from rich.pretty import pprint
# from rich import print
from rich.progress import track
from pathlib import Path
import requests
import gzip

import xmltodict, json

__mesh_files = ['desc2023.gz']


def run():
    client = MongoClient('localhost', 27017)
    client.drop_database('mesh')
    mesh_collection = client.mesh.mesh

    nih_url_base = 'https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/'
    working_dir  = Path('/workspace/mesh_downloads_temp/')
    working_dir.mkdir(exist_ok=True, parents=True)

    for mesh_file in __mesh_files:
        url = nih_url_base + mesh_file
        tmp = working_dir / mesh_file
        if not tmp.is_file():
            with requests.get(url, stream=True) as stream:
                stream.raise_for_status()
                with gzip.open(tmp, 'wb') as f:
                    for chunk in stream.iter_content(chunk_size=8192):
                        f.write(chunk)
        # If not using xmltodict to skip depth
        print('Parsing XML', flush=True)
        with gzip.open(tmp) as infile:
            MeSH = xmltodict.parse(infile)
            print(MeSH.keys(), flush=True)
            print(MeSH['DescriptorRecordSet'].keys(), flush=True)
            MeSH = MeSH['DescriptorRecordSet']['DescriptorRecord']
            print(len(MeSH))
            print('Inserting to database', flush=True)
            mesh_collection.insert_many(track(MeSH, total=len(MeSH), description='Parsing MeSH Terms'))
