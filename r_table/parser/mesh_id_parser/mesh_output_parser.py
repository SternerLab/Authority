import argparse
import sys
sys.path.append('../../')
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client
import json

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="path of output folder to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.file
    return zip_file


def store_to_db(sql_client, output_file):
    output_str = ""

    with open(output_file, 'r') as f:
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
        # break

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

sql_client = sqlite_client()
# sql_client.connect_to_db('test1')

for subdir, dirs, files in os.walk(folder):
        for file in files:
            output_file = subdir + os.sep + file
            store_to_db(sql_client, output_file)
