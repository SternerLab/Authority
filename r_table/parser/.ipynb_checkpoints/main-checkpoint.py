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


#parse command line arguments. usage: python .\main.py --zip_file ./systzool.zip
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip_file", help="file path of zip file to parse and process", required=False)
    parser.add_argument("--folder", help="file path of zip file to parse and process", required=False)
    args = parser.parse_args()
    zip_file = args.zip_file
    folder = args.folder
    return zip_file, folder


#parse xml files and store them in database
def parse_xml_files_to_database_from_zip(zip_file, sql_client, mesh_folder):
    with ZipFile(zip_file, 'r') as zip_obj:
        listOfFiles = zip_obj.namelist()

        for file in listOfFiles:
            if(file.endswith('.xml')):
                zip_obj.extract(file, 'temp')
                try:
                    mesh_filename = file.split('/')[0]
                    filename = mesh_folder+"/"+mesh_filename+".txt"
#                     if not os.path.exists(filename):
#                         os.makedirs(filename)
                    articles = xml_parser.parse('./temp/'+file, filename)
                    insert_article_to_db(articles, sql_client, file)
                    
                except Exception as e:
                    print(str(e))
                    with open("file_parsing_exceptions.txt","a+") as f:
                        f.write('Exception parsing zip file '+zip_file+' and file '+file+'\n')
                        f.write("------------------------------------------------------\n")
                        
        shutil.rmtree('temp') 


def insert_article_to_db(articles, sql_client, file):
    insert_articles_query = "INSERT INTO articles (id, position, last_name, first_initial, middle_initial, suffix, title, journal_name, fullname, first_name, middle_name, language, authors, mesh_terms, affiliation,full_title,year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    for article in articles:
        values = article.__repr__()
        try:
            sql_client.insert_row(insert_articles_query, values)
        except Exception as e:
            print("Exception while inserting article")
            if('Duplicate entry' in str(e)):
                print(str(e))
                print(file)
            else:
                raise


def parse_xml_files_to_database_from_folder(folder, sql_client, mesh_folder):
    print("parsing folder", folder)
    filepath = ''
    for subdir, dirs, files in os.walk(folder):
        print(files)
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".xml"):
                try:
                    mesh_filename = filepath.split('/')[5] #todo: remove parsing folders.
                    filename = mesh_folder+"/"+mesh_filename+".txt"
                    articles = xml_parser.parse(filepath, filename)
                    insert_article_to_db(articles, sql_client, file) 
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

#create table 'Articles'
create_table_query = 'CREATE TABLE IF NOT EXISTS {} (id VARCHAR(255) NOT NULL, position INTEGER, last_name VARCHAR(255), first_initial VARCHAR(255), middle_initial VARCHAR(255), suffix VARCHAR(255), title LONGTEXT, journal_name VARCHAR(255), fullname VARCHAR(255), first_name VARCHAR(255), middle_name VARCHAR(255), language VARCHAR(255),authors LONGTEXT, mesh_terms LONGTEXT, affiliation LONGTEXT, full_title LONGTEXT,year INTEGER, CONSTRAINT PK PRIMARY KEY(id, position))'.format(table_name)

sql_client.execute(create_table_query)

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

