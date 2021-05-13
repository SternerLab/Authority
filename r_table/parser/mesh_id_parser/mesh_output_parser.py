import argparse
import sys
sys.path.append('../../')
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client
import json
import os

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="path of output folder to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.file
    return zip_file


def store_to_db(sql_client, output_file):
    output_str = ""
    
    with open('mesh_log.txt', 'a+') as f:
        f.write(output_file)
        f.write('\n')
        
    with open(output_file, 'r', encoding='windows-1252') as f:
        output_str_list = f.readlines()
        f.close()

    query = 'update articles set mesh_terms = \'{}\' where id = \'{}\''

    id_mesh = {}
    stop_words = ["human","male","female","animal","adult","support non-u.s. gov’t","middle age","aged","english abstract","support u.s. gov’t p.h.s.","case report","rats","comparative study","adolescence","child","mice","time factors","child preschool","pregnancy","united states","infant","molecular sequencedata","kinetics","support u.s. gov’t non-p.h.s.","infant newborn"]

    for line in output_str_list:
        line_split = line.split('|')
        if len(line_split) > 1:
            _id = line_split[0]
            mesh = line_split[1]
            if mesh not in stop_words:
                if _id not in id_mesh:
                    id_mesh[_id] = mesh
                else:
                    id_mesh[_id] += ','+mesh

    for key in id_mesh.keys():
        value = id_mesh[key].replace('\'','\'\'')
        query_f = query.format(value, key) #json.dumps to escape ' characters

        try:
            sql_client.execute(query_f)
            sql_client.connection.commit()
        except Exception as e: #handle any exceptions manually for now. todo
            print(e)
            print(query_f)
            print(key)


folder = parse_arguments()

#inputs and constants
database_path = "../../../database/jstor-authority.db"
table_name = "articles"

#create connection to db
sql_client = sqlite_client(database_path)

with open('mesh_log.txt', 'r') as f:
    files_read = f.readlines()

print(files_read[0])

new_files_read = [ x.strip() for x in files_read]

for subdir, dirs, files in os.walk(folder):
    for file in files:
        output_file = subdir + os.sep + file
        print(output_file)
        # to ensure parsing files that were not parsed before
        if output_file in new_files_read:
            print("file already parsed")
        else:
            print("file not parsed yet. parsing..")
            store_to_db(sql_client, output_file)
