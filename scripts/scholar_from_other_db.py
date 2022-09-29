from .scholar_from_previous_db import *

table = 'google_scholar'

def run():
    mongo_client = MongoClient('localhost', 27017)

    sql_client   = sqlite3.connect('xml_article_data/google_scholar/test3.db')
    sql_cursor   = sql_client.cursor()

    jstor_database    = mongo_client.jstor_database
    scholar_db        = mongo_client.google_scholar
    scholar_jstor_doi = scholar_db.jstor_doi
    scholar_authors   = scholar_db.authors
    articles          = jstor_database.articles

    scholar_db.drop_collection('jstor_doi')

    sql_cursor.execute(all_rows.format(table))
    count = 0
    for scholar_id, name, dois in sql_cursor.fetchall():
        count += 1
        scholar_jstor_doi.insert_one(expand_author_row((None, dois, name, scholar_id), articles))
    print(count)

