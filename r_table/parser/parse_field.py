import argparse
from zipfile import ZipFile
import json

import sys
sys.path.append('../')
from SQL.sqlite_client import sqlite_client
import xml_parser as xml_parser
import os
import shutil 
import time
import xml.etree.ElementTree as ET 



#parse command line arguments. usage: python .\main.py --zip_file ./systzool.zip
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip_file", help="file path of zip file to parse and process", required=False)
    parser.add_argument("--folder", help="file path of zip file to parse and process", required=False)
    args = parser.parse_args()
    zip_file = args.zip_file
    folder = args.folder
    return zip_file, folder


def parse_and_store_field(xmlfile):
    tree = ET.parse(xmlfile)
    article = tree.getroot()
    article_meta = article.find('./front/article-meta')
    id = article_meta.find('./article-id').text
    year = int(article_meta.find('./pub-date/year').text)
    update_db_query = "update articles set year = {} where id = {}".format(year, id)
    sql_client.execute(update_db_query)



#parse xml files and store them in database
def parse_xml_files_to_database_from_zip(zip_file, sql_client, mesh_folder):
    with ZipFile(zip_file, 'r') as zip_obj:
        listOfFiles = zip_obj.namelist()

        for file in listOfFiles:
            if(file.endswith('.xml')):
                zip_obj.extract(file, 'temp')
                try:
                    parse_and_store_field('./temp/'+file)
                except Exception as e:
                    print(str(e))
                    with open("file_parsing_exceptions.txt","a+") as f:
                        f.write('Exception parsing zip file '+zip_file+' and file '+file+'\n')
                        f.write("------------------------------------------------------\n")
                        
        shutil.rmtree('temp') 


def parse_xml_files_to_database_from_folder(folder, sql_client, mesh_folder):
    print("parsing folder", folder)
    filepath = ''
    for subdir, dirs, files in os.walk(folder):
        print(files)
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".xml"):
                try:
                    parse_and_store_field('./temp/'+file)
                except Exception as e:
                    print(str(e))
                    with open("file_parsing_exceptions_"+folder+"_.txt","a+") as f:
                        f.write('Exception parsing folder '+folder+' and file '+filepath+'\n')
                        f.write("------------------------------------------------------\n")
                        
                

start_time = time.time()

#inputs and constants
database_path = "../../database/jstor-authority.db"
table_name = "articles"

#create connection to db
sql_client = sqlite_client(database_path)

zip_file, folder = parse_arguments()

mesh_folder = 'results/mesh'
if not os.path.exists(mesh_folder):
    os.makedirs(mesh_folder)

if zip_file is not None:
    parse_xml_files_to_database_from_zip(zip_file, sql_client, mesh_folder)
    time_taken = "---seconds ---"+ str(time.time() - start_time)
    with open("parserlog.txt", "a+") as f:
        f.write("done parsing zip: "+zip_file+"  time_taken:  "+time_taken+"\n")
elif folder is not None:
    if os.path.exists(folder):
        parse_xml_files_to_database_from_folder(folder, sql_client, mesh_folder)
        with open("parserlog.txt", "a+") as f:
            f.write("done parsing folder: "+folder+"  time_taken:  "+time_taken+"\n")
    else:
        print("folder doesnot exists")
else:
    print("provide zip file or folder file to parse")

