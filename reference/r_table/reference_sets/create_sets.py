import sys
sys.path.append('../')
from SQL.sqlite_client import sqlite_client


sql_client = sqlite_client('../../database/jstor-authority.db')

article_m_records_sql_file = './sql/article_match_records.sql'
sql_client.execute_sql_file(article_m_records_sql_file)

article_match_sql_file = './sql/article_match.sql'
sql_client.execute_sql_file(article_match_sql_file)

article_nm_records_sql_file = './sql/article_non_match_records.sql'
sql_client.execute_sql_file(article_nm_records_sql_file)

article_non_match_sql_file = './sql/article_non_match.sql'
sql_client.execute_sql_file(article_non_match_sql_file)

name_set_records_sql_file = './sql/name_mixed_records.sql'
sql_client.execute_sql_file(name_set_records_sql_file)

name_set_sql_file = './sql/name_mixed_set.sql'
sql_client.execute_sql_file(name_set_sql_file)

firstname_match_records_sql_file = './sql/firstname_match_records.sql'
sql_client.execute_sql_file(firstname_match_records_sql_file)

firstname_nonmatch_records_sql_file = './sql/firstname_nonmatch_records.sql'
sql_client.execute_sql_file(firstname_nonmatch_records_sql_file)

firstname_match_sql_file = './sql/firstname_match.sql'
sql_client.execute_sql_file(firstname_match_sql_file)

firstname_nonmatch_sql_file = './sql/firstname_nonmatch.sql'
sql_client.execute_sql_file(firstname_nonmatch_sql_file)

