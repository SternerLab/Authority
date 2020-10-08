import sys
sys.path.append('../')
# from . import SQLClient
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client

sql_client = sqlite_client()
# sql_client.connect_to_db("test1")

sql_client.execute('drop view article_match')
sql_client.execute('drop view article_non_match')
sql_client.execute('drop view name_set')
