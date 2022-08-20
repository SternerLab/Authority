import sys
sys.path.append('../')
# from . import SQLClient
# from SQL.SQLClient import SQLClient
from SQL.sqlite_client import sqlite_client

sql_client = sqlite_client('../../database/jstor-authority.db')
# sql_client.connect_to_db("test1")

# sql_client.execute('drop view article_match')
sql_client.execute('drop view article_m_records')


# sql_client.execute('drop view article_nm_records')
# sql_client.execute('drop view article_non_match')

sql_client.execute('drop view name_records')
sql_client.execute('drop view name_set')

sql_client.execute('drop view firstname_m_records')
sql_client.execute('drop view firstname_match_set')

# sql_client.execute('drop view firstname_nm_records')
# sql_client.execute('drop view firstname_nonmatch_set')
