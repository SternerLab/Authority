import sys
sys.path.append('../../')
from SQL.SQLClient import SQLClient
import argparse
from zipfile import ZipFile
import os
import xml.etree.ElementTree as ET 


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip_file", help="file path of zip file to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.zip_file
    return zip_file


def parse(xmlfile):
    tree = ET.parse(xmlfile)
    article = tree.getroot()
    article_meta = article.find('./front/article-meta')
    unique_id = article_meta.find('./article-id').text

    article_title = article_meta.find('./title-group/article-title').text
    abstract = article_meta.find('./abstract/p')
    if abstract is not None:
        return unique_id, abstract.text 
    # replace('<p>', '').replace('</p>', '')
    return unique_id,""


# sql_client = SQLClient()
# sql_client.connect_to_db("test1")

zip_file = parse_arguments()
output_dir = '../../results/mesh/input/{}'
# output_dir_num = 0
count = 0
filename = output_dir.format(zip_file)
if not os.path.exists(filename):
    os.makedirs(filename)
f = open(filename+'/input.txt', 'w+')

file_count = 0
abstract_count = 0
non_ascii_count = 0
ascii_count = 0


with ZipFile(zip_file, 'r') as zip_obj:
    listOfFiles = zip_obj.namelist()
    for file in listOfFiles:
        if(file.endswith('.xml')):
            file_count += 1
            if count < 0 :
                #reset count and update output directory
                count = 0
                output_dir_num += 1
                f.close()
                filename = output_dir.format(output_dir_num)
                if not os.path.exists(filename):
                    os.makedirs(filename)
                f = open(filename+'/input.txt', 'w+')
            zip_obj.extract(file, 'temp')
            try:
                _id, abstract = parse('./temp/'+file)
                if abstract != '':
                    abstract_count += 1
                    value = _id + '|' + abstract
                    if is_ascii(value) == False:
                        non_ascii_count+=1
                        value = (value.encode("ascii", "ignore")).decode("utf-8")
                        count+=1
                        f.write(value)
                        f.write('\n')
                    else:
                        ascii_count+=1
            except Exception as e:
                print(str(e))
print("file_count ", str(file_count), " abstract_count ", str(abstract_count), " ascii_count ", str(ascii_count), " non_ascii_count ", str(non_ascii_count))

# with open('../../results/mesh/input/input.txt', 'w', encoding="utf-8") as f:
#     for row in results:
#         value = row[0]+'|'+row[1]
#         if is_ascii(value):
#             f.write(value)
#             f.write('\n')

