from scholarly import scholarly
import sqlite3
from scholarly import ProxyGenerator
import time
import sys
import os.path
import pandas as pd


def insert_record(records, name, name_id):
    # query = "INSERT INTO google_scholar (name_id, fullname, ids) values (?, ?, ?)"
    list_ids = [i[0] for i in records]
    # cursor.execute(query, (name_id, name.replace('\'', '\'\''), ','.join(list_ids)))
    # cnx.commit()
    with open('results_'+index_from+'_'+index_to+'.csv', 'a+') as f:
        f.write(name_id+';'+name.replace('\'', '\'\'')+';'+','.join(list_ids))
        f.write('\n')


#todo: consider other authors.
def put_titles_in_db(titles, name, name_id):
    # query1 = "select * from google_scholar"
    # cursor.execute(query1)
    # print(list(cursor.fetchall()))
    query = "SELECT id, fullname FROM Articles_2_ab where UPPER(full_title) in " + "( "
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
    print(records)
    if len(records) > 0:
        insert_record(records, name, name_id)

    #     print((records))

    # for title in titles:
    #     query = "SELECT * FROM Articles_2 where UPPER(title) "
        
    #     if "'" not in title:
    #         # query = 'SELECT * FROM Articles_2 where title = 'SUN COMPASS ORIENTATION OF PIGEONS UPON EQUATORIAL AND TRANS-EQUATORIAL DISPLACEMENT''
    #         # print(query+title.upper())
    #         cursor.execute(query+'\''+title.upper()+'\'')
    #         records = list(cursor.fetchall())
    #         # print(title)
    #         if len(records) == 1:
    #             print(author[0])
    #             print(records[0])


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
    


def get_top_ten_authors_with_name_match(query, name):
    authors = []
    # print(name)
    name = " ".join(name.split()) #to remove all whitespaces.
    try:
        for i in range(0,10):
            author = (next(query))
            # print(author)
            #match on lastname middle name and first name todo #Douglas C. Andersen
# Andersen, Douglas C. Glenn R. Lopez
# Randall Glenn Lopez, M. S. Johnson and Michael S. Johnson and Michelle S. Johnson and Mathew Mark, Robert L. Smith and Robert L Smith
            if name_matches(author.name, name): 
                authors.append(author)
                print("match found")
            print(author.name)
    except Exception as e:
            print(e)
            with open('failed_gs.txt', 'a' ) as f:
                f.writelines(name)
                f.write('\n')
    return authors

index_from = sys.argv[1]
index_to = sys.argv[2]
filename_log = 'scholarlog.txt'
if os.path.exists(filename_log):
    log_lines = []
    with open(filename_log, 'r') as f:
        log_lines = f.readlines()
        last_read = log_lines[len(log_lines)-1]
        last_read_index = last_read.split(':')[1]
        index_from = last_read_index.strip()

print("index_from",index_from)
print('results_'+index_from+'_'+index_to+'.csv')


# query1 = "drop table google_scholar"
# cursor.execute(query1)
create_table_query = "CREATE TABLE IF NOT EXISTS google_scholar (name_id VARCHAR(255) NOT NULL,  fullname VARCHAR(255) NOT NULL, ids VARCHAR(255) NOT NULL)"
cursor.execute(create_table_query)

dfs = pd.read_csv("authors.csv")
authors = dfs["fullname"].to_list()
authors = [(x,0) for x in authors]

# authors = [('wayne maddison',0)]

query1 = "select count(*) from google_scholar"
cursor.execute(query1)
print(list(cursor.fetchall()))
# print(authors.index(("Jennifer Nerissa Davis",0)))
# index = [x for x, y in enumerate(authors) if y[0] == "Mary  Meagher"]
# print(index)


# pg = ProxyGenerator()
# pg.FreeProxies()
# scholarly.use_proxy(pg)
count = 1
i = int(index_from)
for name in authors[(int(index_from)):(int(index_to))]:
    # name = 'wayne maddison'
    try:
        print(name[0])
        with open(filename_log, 'a+') as f1:
            f1.write(name[0]+':'+str(i))
            i+=1
            f1.write('\n')
        search_query = scholarly.search_author(name[0])
        authors = search_query
        authors_list = get_top_ten_authors_with_name_match(search_query, name[0])
        for author in authors_list:
            print(author)
            author_object = author.fill(sections=['publications'])
            publications = author_object.publications
            titles = [i.bib['title'] for i in publications]
            put_titles_in_db(titles, name[0], author_object.id)
        time.sleep(30)
        count+=1
        if count%50 == 0:
            time.sleep(50)
#             pg = ProxyGenerator()
#             pg.FreeProxies()
#             scholarly.use_proxy(pg)
        print(count)
    except Exception as e:
        print("________________________________________________________________")
        print(e)
        # with open('failed_gs.txt', 'a+' ) as f:
        #     f.writelines(name[0])
        #     f.write('\n')
    # print(authors_list)
    # for i in range(0,1):
    #     try:
    #         author = (next(authors))
    #         Author_obj = author.fill(sections=['publications'])
    #         # if author.name == 'Sunniva M.D. Aagaard':
    #         #     authors_list.append(author)
    #         # else: 
    #         # print(author)
    #         print(".....................................")
    #         publications = Author_obj.publications
    #         # with open('sch.txt', 'w+') as f:
    #         #     f.write(str(publications))
    #         # print(publications[0].bib['title'])
    #         titles = [i.bib['title'] for i in publications]
    #         print(len(titles))
    #         # print(".................................")
    #         put_titles_in_db(titles, name[0])

    #     except Exception as e:
    #         print(str(e))

    # break

    # print(authors_list)