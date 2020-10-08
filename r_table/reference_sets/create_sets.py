import sys
sys.path.append('../')
# from . import SQLClient
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client


sql_client = sqlite_client()
# sql_client.connect_to_db("test1")

article_match_sql_file = './sql/article_match.sql'
sql_client.execute_sql_file(article_match_sql_file)

article_non_match_sql_file = './sql/article_non_match.sql'
sql_client.execute_sql_file(article_non_match_sql_file)

name_set_sql_file = './sql/name_mixed_set.sql'
sql_client.execute_sql_file(name_set_sql_file)