import sqlite3
from rich.pretty import pprint
from rich import print

all_tables   = "SELECT name FROM sqlite_master WHERE type='table'"
all_rows     = 'SELECT * from {}'
all_views    = "SELECT * from sqlite_master WHERE type='view'"
show_columns = 'PRAGMA table_info({});'

def run():
    connection = sqlite3.connect('/workspace/jstor_other/google_scholar/test3.db')
    # connection = sqlite3.connect('xml_article_data/google_scholar/test3.db')
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
        cursor.execute(all_rows.format(sel))
        rows = cursor.fetchall()
        i = 0
        for row in rows:
            i += 1
        print(f'Total: {i}')
