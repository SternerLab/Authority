import argparse
from zipfile import ZipFile


import sys
sys.path.append('../')
from SQL.SQLClient import SQLClient
import xml_parser as xml_parser


#parse command line arguments. usage: python .\main.py --zip_file ./systzool.zip
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip_file", help="file path of zip file to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.zip_file
    return zip_file


#parse xml files and store them in database
def parse_xml_files_to_database(zip_file, sql_client):
    with ZipFile(zip_file, 'r') as zip_obj:
        listOfFiles = zip_obj.namelist()
    
        insert_articles_query = "INSERT INTO Articles (id, position, last_name, first_initial, middle_initial, suffix, title, journal_name, fullname, first_name, middle_name, language, authors) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for file in listOfFiles:
            if(file.endswith('.xml')):
                zip_obj.extract(file, 'temp')
                articles = xml_parser.parse('./temp/'+file)
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


#create connection to db
sql_client = SQLClient()
sql_client.connect_to_db("test1")

#create table 'Articles'
create_table_query = 'CREATE TABLE IF NOT EXISTS Articles (id VARCHAR(255) NOT NULL, position INTEGER, last_name VARCHAR(255), first_initial VARCHAR(255), middle_initial VARCHAR(255), suffix VARCHAR(255), title LONGTEXT, journal_name VARCHAR(255), fullname VARCHAR(255), first_name VARCHAR(255), middle_name VARCHAR(255), language VARCHAR(255),authors LONGTEXT, CONSTRAINT PK PRIMARY KEY(id, position))'
sql_client.execute(create_table_query)

zip_file = parse_arguments()
parse_xml_files_to_database(zip_file, sql_client)