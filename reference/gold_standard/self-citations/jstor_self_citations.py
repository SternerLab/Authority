import xml.etree.ElementTree as ET 
import sqlite3
import os
import shutil 
from zipfile import ZipFile


#todo rename columns
def insert_to_db(titles, unique_id):
    # print(titles)
    query = "select distinct(authors) from articles where id= '"+ unique_id +"'"
    cursor.execute(query)
    records = cursor.fetchall() #[('Andrew P. Martin,Theresa M. Burg',)]  #Authors of the current paper unique_id.
    records_str = ','.join(str(y) for x in records for y in x if len(x) > 0) #Andrew P. Martin,Theresa M. Burg
#     print(records_str)

    for record in records_str.split(','):
        try:
            get_current_ids_query = "select ids from self_citation_jstor where full_name='"+ record +"'"
            cursor.execute(get_current_ids_query)
            ids_str_list = list(cursor.fetchall())
            # ids_str=""
#             print(ids_str_list)
            if len(ids_str_list) > 0:
                ids = set(ids_str_list[0][0].split(','))
            else:
                ids = set()
            ids.add(unique_id)
#             print(ids)
            query = "select full_title,id from articles where fullname='"+ record +"'" #get all titles of the given author.
            cursor.execute(query)
            author_records = list(cursor.fetchall())
            for title in titles:
                for author_record in author_records:
                    if author_record[0] in title: #check if author's titles in main db is present in self cited papers.
                        ids.add(author_record[1])
                        print("match found")
            insert_query = "INSERT INTO self_citation_jstor (ids, full_name) VALUES (?,?)"
            cursor.execute(insert_query,(",".join(ids), record))
            cnx.commit()
#             with open('results_self_.csv', 'a+') as f:
#                 f.write(ids+';'+full_name.replace('\'', '\'\''))
#                 f.write('\n')
        except Exception as e:
            print(e)


def get_authors(unique_id)->list:
    query = "select distinct(authors) from articles where id='{}'".format(unique_id)
    cursor.execute(query)
    return list(cursor.fetchall()[0])
    

def get_title_id(title):
    query = "select distinct(id) from articles where full_title='{}'".format(title)
    cursor.execute(query)
    return list(cursor.fetchall()[0])


def store_self_citation(unique_id, citation_id, common_author):
    query = "insert into self_citations (ids, full_name) values (?,?)"
    cursor.execute(query,unique_id+","+citation_id,common_author)
    cnx.commit()
    print("stored {}+" , "+{} :".format(unique_id, citation_id), common_author)


def insert_to_db(citation_titles, unique_id):
    authors = get_authors(unique_id)
    for citation_title in citation_titles:
        citation_id = get_title_id(citation_title)
        if citation_id is not None:
            citation_authors = get_authors(citation_id)
            common_authors = list(set(authors) & set(citation_authors))
            if len(common_authors)>0:
                for common_author in common_authors:
                    store_self_citation(unique_id, citation_id, common_author)
    
            

def parse_xml_files_to_database_from_folder(folder,new_count, prev_count, total_count):
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(".xml"):
                if new_count >= prev_count:
                    total_count+=1
                    try:
                        print(filepath)
                        parse_citations(filepath)
                        with open('log_self_citation.txt', 'w') as f:
                            f.write(str(total_count))
                    except Exception as e:
                        print(str(e))
                new_count+=1


        

def parse_citations(xmlfile):
    tree = ET.parse(xmlfile)
    article = tree.getroot()
    back = article.find('./back')
    article_meta = article.find('./front/article-meta')
    unique_id = article_meta.find('./article-id').text
    no_of_articles_with_citations = 0
    no_of_articles_with_self_citations = 0
    titles = []
    if back is not None:
        for i in back.findall('./ref-list/ref'):
            titles.append(getTitle(i.find('./mixed-citation').text))
#         print(len(back.findall('./ref-list')))
        insert_to_db(titles, unique_id)
        # break


def getTitle(text):
    text = text.strip()
    return text
    # words = text.split('.')
    # for i,word in enumerate(words):
    #     word = word.strip()
    #     if word.isnumeric():
    #         # print(word,i)
    #         title = words[i+1]
    #         title = title.replace("\n", ' ')
    #         print(title)
    #         if title is not None:
    #             return title
    
    

folder = "../../../data/qrstuvwyz"

#create table for pairs of articles
cnx = sqlite3.connect('../../../database/jstor-authority.db')
cursor = cnx.cursor()

# drop = "drop table self_citation_jstor"
# cursor.execute(drop)
query = 'create table if not exists self_citation_jstor (ids VARCHAR(255) NOT NULL, full_name VARCHAR(255) NOT NULL)'
cursor.execute(query)

log = '0'
try:
    with open('log_self_citation.txt', 'r') as f:
        log_lines = f.readlines()
        log = log_lines[0].strip()
except:
    print('.')

prev_count = int(log)
new_count = 0
total_count = prev_count

                
def parse_xml_files_to_database_from_zip(zip_file, new_count, prev_count, total_count):
    print(new_count)
#     print(prev_count)
#     print(total_count)
#     datapath = '../../AUthority'

    with ZipFile(zip_file, 'r') as zip_obj:
        listOfFiles = zip_obj.namelist()
    

        for file in listOfFiles:
            if(file.endswith('.xml')):
                if new_count >= prev_count:
                    zip_obj.extract(file, 'temp')
                    total_count+=1
                    try:
                        print('temp/'+file)
                        parse_citations('temp/'+file)
                        with open('log_self_citation.txt', 'w') as f:
                            f.write(str(total_count))
                    except Exception as e:
                        print(str(e))
                new_count+=1
        try:
            shutil.rmtree('temp') 
        except:
            pass
                
#         with open('log.json' , 'w+') as f:
#             json.dump(mesh_dict, f)
#         print(count)
        

# parse_xml_files_to_database_from_zip(folder, new_count, prev_count, total_count)

parse_xml_files_to_database_from_folder(folder,new_count,prev_count,total_count)
# folder = "../../Authority/data/receipt-id-561931-jcodes-klmnop-part-002.zip"
# prev_count = 0
# parse_xml_files_to_database_from_zip(folder, new_count, prev_count, total_count)