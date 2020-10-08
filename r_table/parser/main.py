import argparse
from zipfile import ZipFile
import json

import sys
sys.path.append('../')
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client
import xml_parser as xml_parser
import os



#parse command line arguments. usage: python .\main.py --zip_file ./systzool.zip
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip_file", help="file path of zip file to parse and process", required=False)
    parser.add_argument("--folder", help="file path of zip file to parse and process", required=False)
    parser.add_argument("--mesh_filename", help="file path of zip file to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.zip_file
    folder = args.folder
    mesh_filename = args.mesh_filename
    return zip_file, folder, mesh_filename


#parse xml files and store them in database
def parse_xml_files_to_database_from_zip(zip_file, sql_client, mesh_file):
    mesh_dict = {}
    count = 0

    with ZipFile(zip_file, 'r') as zip_obj:
        listOfFiles = zip_obj.namelist()
    

        for file in listOfFiles:
            if(file.endswith('.xml')):
                zip_obj.extract(file, 'temp')
                try:
                    articles = xml_parser.parse('./temp/'+file, mesh_file)
                    insert_article_to_db(articles, sql_client, file)
                except Exception as e:
                    print(str(e))
                
        with open('mesh_taxon.json' , 'w+') as f:
            json.dump(mesh_dict, f)
        print(count)

def insert_article_to_db(articles, sql_client, file):
    # insert_articles_query = "INSERT INTO Articles_2 (id, position, last_name, first_initial, middle_initial, suffix, title, journal_name, fullname, first_name, middle_name, language, authors, mesh_terms, affiliation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insert_articles_query = "INSERT INTO Articles_2 (id, position, last_name, first_initial, middle_initial, suffix, title, journal_name, fullname, first_name, middle_name, language, authors, mesh_terms, affiliation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    for article in articles:
        values = article.__repr__()
        try:
            sql_client.insert_row(insert_articles_query, values)
        except Exception as e:
            if('Duplicate entry' in str(e)):
                print(str(e))
                print(file)
            else:
                raise


def parse_xml_files_to_database_from_folder(folder, sql_client, mesh_file):
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".xml"):
                try:
                    articles = xml_parser.parse(filepath, mesh_file)
                    insert_article_to_db(articles, sql_client, file)
                except Exception as e:
                    print(str(e))
                break


#create connection to db
sql_client = sqlite_client()
# sql_client.connect_to_db("test1")

#create table 'Articles'
create_table_query = 'CREATE TABLE IF NOT EXISTS Articles_2 (id VARCHAR(255) NOT NULL, position INTEGER, last_name VARCHAR(255), first_initial VARCHAR(255), middle_initial VARCHAR(255), suffix VARCHAR(255), title LONGTEXT, journal_name VARCHAR(255), fullname VARCHAR(255), first_name VARCHAR(255), middle_name VARCHAR(255), language VARCHAR(255),authors LONGTEXT, mesh_terms LONGTEXT, affiliation LONGTEXT, CONSTRAINT PK PRIMARY KEY(id, position))'
sql_client.execute(create_table_query)

zip_file, folder, mesh_filename = parse_arguments()

output_dir = 'C:/Users/manuh/Documents/sterner lab/AuthorDisambiguation/r_table/results/mesh/{}'
filename = output_dir.format(mesh_filename)
if not os.path.exists(filename):
    os.makedirs(filename)
f = open(filename+'/input.txt', 'w+')
print(filename+'/input.txt')


if zip_file is not None:
    parse_xml_files_to_database_from_zip(zip_file, sql_client, f)
elif folder is not None:
    parse_xml_files_to_database_from_folder(folder, sql_client, f)
else:
    print("provide zip file or folder file to parse")

f.close()