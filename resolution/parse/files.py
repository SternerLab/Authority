from zipfile import ZipFile
import json
import os
import shutil
from pathlib import Path

def iter_xml_files(zip_file):
    with ZipFile(zip_file, 'r') as zip_obj:
        temp = Path('temp')
        temp.mkdir(exist_ok=True)
        try:
            listOfFiles = zip_obj.namelist()
            yield len(listOfFiles)
            for file in listOfFiles:
                if file.endswith('.xml'):
                    zip_obj.extract(file, 'temp')
                    yield f'./temp/{file}'
        finally:
            shutil.rmtree('temp')


''
