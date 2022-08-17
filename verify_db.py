import sqlite3

all_tables   = "SELECT name FROM sqlite_master WHERE type='table'"
all_rows     = 'SELECT * from {}'
show_columns = 'PRAGMA table_info({});'

connection = sqlite3.connect('database/jstor-authority.db')
cursor     = connection.cursor()
tables     = [t[0] for t in cursor.execute(all_tables).fetchall()]
for table in tables:
    print('-' * 80)
    print(table)
    print('-' * 80)
    cursor.execute(show_columns.format(table))
    print(cursor.fetchall())
    cursor.execute(all_rows.format(table))
    rows = cursor.fetchall()
    print(len(rows))
    if len(rows) >= 5:
        for i in range(5):
            print('Ex ({i}): ', rows[i])
    print()
