import sqlite3
import requests
import json


def insert_record(records, name, name_id):
    query = "INSERT INTO bhl (name_id, fullname, ids) values (?, ?, ?)"
    list_ids = [i[0] for i in records]
    cursor.execute(query, (name_id, name, ','.join(list_ids)))
    cnx.commit()


#todo: consider other authors.
def put_titles_in_db(titles, name, name_id):
    # query1 = "select * from google_scholar"
    # cursor.execute(query1)
    # print(list(cursor.fetchall()))
    query = "SELECT id, fullname FROM articles where UPPER(title_full) in " + "( "
    for title in titles:
        title = title.replace('\'', '\'\'').upper()
        query += "\'"+title+"\'" + ","
    query=query[:-1]
    query += " )"
    query += " and fullname= '{}'".format(name.replace('\'', '\'\''))
    # print(query)
    cursor.execute(query)
    records = list(cursor.fetchall())
    print(len(records))
    # print(records)
    if len(records) > 0:
        insert_record(records, name, name_id)


def name_matches(gs_name, db_name):
    #direct name match or words interchange match or if three words in name, first intial middle initial and last name match.
    if(gs_name == db_name):
        return True
    gs_name = gs_name.replace(',', '')
    gs_name = gs_name.replace('.', '')
    db_name = db_name.replace('.', '')
    db_name = db_name.replace('.', '')
    gs_name_list = gs_name.split(' ')
    db_name_list = db_name.split(' ')
    intersection = list(set(db_name_list) & set(gs_name_list))
    if(len(intersection) == len(db_name_list) & len(intersection) == len(gs_name_list)):
        return True


cnx = sqlite3.connect('../../../database/jstor-authority.db')
cursor = cnx.cursor()

# drop_table = 'drop table bhl'
# cursor.execute(drop_table)

create_table_query = "CREATE TABLE IF NOT EXISTS bhl (name_id VARCHAR(255) NOT NULL, fullname VARCHAR(255) NOT NULL, ids VARCHAR(255) NOT NULL)"
cursor.execute(create_table_query)

query = 'select distinct(fullname) from articles'
cursor.execute(query)
authors=list(cursor.fetchall())
print(len(authors))
# index = [x for x, y in enumerate(authors) if y[0] == "R.  Bauch"]
# print(index)


author_search_api = 'https://www.biodiversitylibrary.org/api3?op=AuthorSearch&authorname={0}&apikey=348a0e17-b8b9-42f5-b9d1-931c6aa2d73b&format=json'
author_metadata_api = 'https://www.biodiversitylibrary.org/api3?op=GetAuthorMetadata&id={0}&pubs=t&apikey=348a0e17-b8b9-42f5-b9d1-931c6aa2d73b&format=json'
for author in authors:
    try:
        print(author)
        author_search_api_ = author_search_api.format(author[0])
        response = requests.get(author_search_api_).json()
        # print(author[0]) 
        if response["Status"] == 'ok' and response['ErrorMessage'] == '' and len(response['Result']) == 1:
            # print(response['Result'])
            results = response['Result']
            for result in results:
                if name_matches(result['Name'],author[0]):
                    print("match found")
                    # result = response['Result'][0]
                    AuthorId = result['AuthorID']
                    author_metadata_api_ = author_metadata_api.format(AuthorId)
                    metadata_response = requests.get(author_metadata_api_).json()
                    # print(metadata_response)
                    if metadata_response['Status'] == 'ok' and metadata_response['ErrorMessage'] == '':
                        Result = metadata_response['Result']
                        publications = Result[0]['Publications']
                        titles = [i['Title'] for i in publications]
                        put_titles_in_db(titles, author[0], AuthorId)
                print(result['Name'])
                # print(titles)
        with open('bhl.txt', 'a+') as f:
            f.writelines(author)
            f.write('\n')
    except Exception as e:
        print(e)

        # break
    # else:
    #     print(len(response['Result']))
    #     print(response['Status'])
        # print(response['ErrorMessage'])