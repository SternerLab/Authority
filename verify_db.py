import sqlite3
from rich.pretty import pprint

all_tables   = "SELECT name FROM sqlite_master WHERE type='table'"
all_rows     = 'SELECT * from {}'
all_views    = "SELECT * from sqlite_master WHERE type='view'"
show_columns = 'PRAGMA table_info({});'

connection = sqlite3.connect('database/jstor-authority.db')
cursor     = connection.cursor()
views      = cursor.execute(all_views).fetchall()
selectable = [('table', t[0]) for t in cursor.execute(all_tables).fetchall()]
selectable.extend([('view', t[1]) for t in views])

pprint(selectable)

for kind, sel in selectable:
    print('-' * 80)
    print(f'{kind}: {sel}')
    print('-' * 80)
    cursor.execute(show_columns.format(sel))
    print(cursor.fetchall())
    cursor.execute(all_rows.format(sel))
    rows = cursor.fetchall()
    # print(len(rows))
    # if len(rows) >= 5:
    try:
        for i in range(5):
            print('Ex ({i}): ', rows[i])
    except IndexError:
        print('{sel} has no rows')
    print()

authors = "SELECT last_name,first_initial,first_name,middle_name,full_title FROM articles WHERE last_name='Smith' ORDER BY last_name,first_name"
for last_name, first_initial, first_name, middle_name, title in cursor.execute(authors).fetchall():
    print(f'{last_name:20} {first_initial:1} {first_name:20}:    {title[:30]}')
