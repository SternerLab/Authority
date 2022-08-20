import sqlite3
import pandas as pd
import ast
import time
import json
import collections


'''
Let TP = total number of pairs (of author names) correctly put into same cluster, 
TN = total number of pairs correctly put into different clusters,
 FP = total number of pairs incorrectly put into same cluster and 
 FN = total number of pairs incorrectly put into different clusters. Let S = TP + TN + FP + FN .
1. Accuracy=(TP+TN/S). It is the ratio of the number of correctly clustered pairs to the total number of pairs.
2. Pairwise precision pp = TP/(TP + FP). It is the fraction of pairs in a cluster being co-referent.
3. Pairwise recall pr = TP/(TP + FN ). It is the fraction of co-referent pairs that are put in the same cluster.
4. Pairwise F1-score pf 1 = (2 × pp × pr)/(pp + pr). It is the harmonic mean of pp and pr.
 Journal of Information Science, 2019, pp. 1–28 Ó The Author(s), DOI: 10.1177/0165551519888605
Sanyal et al. 4
 5. Pairwise lumping error rate PLER = FP/(TP/FP). It is the fraction of pairs in a cluster being non co-referent.
6. Pairwise splitting error rate PSER = FN =(TN + FN ). It is the fraction of co-referent pairs that are split into dif-
ferent clusters.
7. Overall pairwise error rate PER = (FP + FN )=S .


lets say we have <id1,id2>;<id3,id4,id5> clusters
gold standard: <id1, id2>, <id1,id3>. (lumping and splitting)
TP = 1 
TN = 1
FP = 0
FN = 1
S = 3

Accuracy = 2/3
pp = 1
pr = 1/2 

gs and bhl
1.get matching pairs of gold standard data. example: auth1_id1 : p1,p2,p3 and auth1_id2 : p4,p5,p6. pairs => p1,p2; p2,p3; p1,p3; p4,p5; p5,p6; p2,p6
2. get non matching pairs of gold standard data. example: p1,p4; p1,p5; p1,p6; p2,p4; p2,p5; p2,p6; p3,p4; p3,p5; p3,p6;
3.check if matching pair in single cluster: 
    yes=> TP+=1 (no splitting)
    no=> FN+=1 (splitting)
check if non matching pair in single cluster:
    yes=> FP+=1 (lumping)
    no=> TN+=1 (no lumping)


or for each cluster:
    get gold standard data of authors
    create matching and non matching pairs
    get matching pairs and non matching pairs of clusters:
        check intersection with matching pairs = c: => TP+=c and FN+= pairs in cluster-c
        check intersection with non matching pairs = c2: => FP+=c2 and TN+= pairs in cluster-c2



'''
import itertools

  

def get_pairs(list_):
    return itertools.combinations(list_, 2)


def get_pairs_from_two_lists(lista, listb):
    return list(itertools.product(lista, listb))


def have_common_articles(list_):
    final_list = []
    for val in list_:
        list_val = val.split(',')
        
        final_list.extend(list_val)
    if len(final_list) == len(set(final_list)):
        return False
    return True


def write_to_file(data_dict,authornames_to_article_ids,clusters,_id,filename):
    author_data = {} 
    cluster_and_author_data = {}
    for author_name in authornames_to_article_ids.keys():
        # author_name = author_names[author_id]
        if author_name not in author_data:
            author_data[author_name] = []
        author_data[author_name].extend(authornames_to_article_ids[author_name])
        # print("")
    cluster_and_author_data["authors"] = author_data
    cluster_and_author_data["clusters"] = clusters
    data_dict[_id] = cluster_and_author_data
    with open(filename, "w") as f:
        json.dump(data_dict,f)

cnx = sqlite3.connect('../../database/jstor-authority-old-for-plots.db')
cursor = cnx.cursor()

#remove duplicates from clusters db
# cursor.execute("drop table clusters_no_dups")
# cursor.execute("create table clusters_no_dups as select min(first_initial_last_name) as first_initial_last_name, total_records, clusters, total_clusters, authors, author_count from clusters_x10 group by total_records, clusters, total_clusters, authors, author_count")
#remove duplicates from google_scholar db
# cursor.execute("drop table google_scholar_no_dups")
# cursor.execute("create table google_scholar_no_dups as select min(name_id) as name_id, fullname, ids from google_scholar group by fullname, ids")

# print(pd.read_sql_query("select count(name_id) as c, fullname from google_scholar group by fullname having c>1 order by c desc",cnx))
# print(pd.read_sql_query("select * from clusters_no_dups where authors like '%Susan M. Haig%'",cnx))


#case 1: block with one author name-> no issues. regular splitting/no splitting case.
#case 2: block with two author names but single author name variant. lumping should be considered in this case. But how? Only full author names to be considered. Preprocessing to remove extra spaces.
#case 3: block with two author names and not name variants. No issues. Seemingly different must not form a single cluster. lumping should be considered here.

#following code to retrieve clusters based on all forename initials and last name (AINI).
query = "select distinct id as clusters, fullname as authors, first_initial, last_name from articles"
old_data = pd.read_sql_query(query,cnx)
data = old_data
data['clusters'] = data.groupby(["first_initial", "last_name"])['clusters'].transform(lambda x : ';'.join(x))
data['authors'] = data.groupby(["first_initial", "last_name"])['authors'].transform(lambda x : ','.join(x))
data = data.drop_duplicates()
clusters_data = data

# print(type(fake_gs_data))
# print(fake_gs_data)
# search_gs_query = "select name_id, replace(fullname, '  ', ' ') as full_name, ids from google_scholar_new where lower(full_name) like '"
search_gs_query = "select name_id, full_name, ids from google_scholar_new where lower(full_name) like '"
total_clusters = 0
total_lumps = 0
total_splits = 0
total_lumping_blocks = 0
total_splitting_blocks = 0
lumping_based_on_name = 0
splitting_based_on_name = 0
authors_per_block_avg = 0
authors_per_block_max = 0
authors_per_block_min = 999
authors_found_in_google_scholar = 0
lumps_data = {}
splits_data = {}
duplicate_author_profiles_on_gs = 0
articles_found_in_google_scholar = 0
TP = 0
TN = 0
FP = 0
FN = 0

for index,row in clusters_data.iterrows():
    #say more than one profile for a same author name. map author id -> db ids.
    # author_name_1 : 1,2,3,4 author_name_2 : 5,6,7. get clusters row["clusters"]. 
    #create map cluster_group_1: 1,2, 4. cluster_group_2: 3,5,6,7. splitting case.

    clusters = row["clusters"].split(',')
#     print(clusters)
    i = 0
    cluster_to_author_map = {}
    author_to_cluster_map = {}
    cluster_to_ids = {}
    author_to_ids = {}
    authorid_to_name = {}
    authornames_to_article_ids = {}
    for cluster in clusters:
        cluster_to_ids[i] = cluster.split(';')
        i+=1
    
    duplicate_author_names = []
    author_names = list(set(row["authors"].strip().split(',')))
#     print(author_names)
    j = 0
    for author in author_names:
        auth_query = search_gs_query+author.strip().replace('\'', '\'\'')+"'"
        author_gs_data = pd.read_sql_query(auth_query,cnx)
        for index, row in author_gs_data.iterrows():
            _id = row["name_id"]
            authorid_to_name[_id] = author
            if _id not in author_to_ids:
                author_to_ids[_id] = []
            article_ids = row["ids"].split(',')
            author_to_ids[_id].extend(article_ids)
            articles_found_in_google_scholar+=len(article_ids)

            #for evaluating the evaluation results purpose.
            if author not in authornames_to_article_ids:
                authornames_to_article_ids[author] = []
            authornames_to_article_ids[author].append(row["ids"])
            j+=1
        if not author_gs_data.empty:
            authors_found_in_google_scholar+=1

    # print(cluster_to_ids)
    # print(author_to_ids)
    # print("...")
    
    #remove duplicate author profile data
    for val in authornames_to_article_ids:
        if len(authornames_to_article_ids[val]) > 1 and have_common_articles(authornames_to_article_ids[val]):
            duplicate_author_profiles_on_gs+=1
            for authid, authname in authorid_to_name.items():
                if authname == val and authid in author_to_ids.keys(): 
                    del author_to_ids[authid]
            with open("duplicate_author_profiles_gs.txt", "a+") as f:
                f.write(val+" : "+str(authornames_to_article_ids[val]))
                f.write("\n")
                
    # check author ids in same group. if not splitting case. check if a cluster has only one author ids. no->lumping case
    # to check: author_name_1: cluster_1, cluster_2 ; author_name_2:cluster_2 ; cluster_1: author_1 ; cluster_2: author_1, author_2 ;
    # splitting, no splitting or lumping; no splitting or lumping; lumping
    i=0
    for cluster_id in cluster_to_ids:
        j=0
        for author_id in author_to_ids:
            cluster_id_values = cluster_to_ids[cluster_id]
            for val in cluster_id_values:
                if val in author_to_ids[author_id]:
                    if i in cluster_to_author_map:
                        cluster_to_author_map[i].add(author_id)
                    else:
                        cluster_to_author_map[i] = set()
                        cluster_to_author_map[i].add(author_id)
                    if author_id in author_to_cluster_map:
                        author_to_cluster_map[author_id].add(i)
                    else:
                        author_to_cluster_map[author_id] = set()
                        author_to_cluster_map[author_id].add(i)
            j+=1
        i+=1
    
#     print(author_to_cluster_map)
#     print(cluster_to_author_map)
#     print("...")

   
    
    isdup = False
    #compute splits and lumps
    for val_ in cluster_to_author_map:
        if len(cluster_to_author_map[val_]) > 1:
            total_lumps+=1
            write_to_file(lumps_data,authornames_to_article_ids,clusters,total_lumps,"lumping_data_gs.json")
            for val in authornames_to_article_ids:
                if len(authornames_to_article_ids[val]) > 1 and have_common_articles(authornames_to_article_ids[val]):

                    duplicate_author_profiles_on_gs+=1
                    isdup = True
                    duplicate_author_names.append(val)
                    total_lumps-=1
                    #remove duplicate profile for further evaluation
                    for authid, authname in authorid_to_name.items():
                        if authname == val and authid in author_to_ids: 
                            del author_to_ids[authid]
                    with open("duplicate_author_profiles.txt", "a+") as f:
                        f.write(val+" : "+str(authornames_to_article_ids[val]))
                        f.write("\n")
    
    for val in author_to_cluster_map:
        if len(author_to_cluster_map[val]) > 1:
            total_splits+=1
            write_to_file(splits_data,authornames_to_article_ids,clusters,total_splits,"splitting_data_gs.json")

    #compute splits and lumps per block
    if isdup == False: #consider only non duplicate profiles.
        for val in cluster_to_author_map:
            if len(cluster_to_author_map[val]) > 1:
                total_lumping_blocks+=1
                break
    
    for val in author_to_cluster_map:
        if len(author_to_cluster_map[val]) > 1:
            total_splitting_blocks+=1
            break

    #lumping and splitting based on name
    total_authors = len(author_names)
    total_clusters = len(clusters)

    if total_authors > total_clusters:
        lumping_based_on_name+=1
    if total_clusters > total_authors:
        splitting_based_on_name+=1

    #authors per block analysis
    authors_per_block_avg += total_authors
    authors_per_block_max = max(total_authors, authors_per_block_max)
    authors_per_block_min = min(total_authors, authors_per_block_min)

     # todo: remove duplicate authors. Let say same individual created two different profiles on google scholar (how do we know same? if they share common papers.)
    # remove both profiles for evaluation. 
    # example: 
    # profile1 -> author_name1 : id1 : paper1, paper2, paper3.
    # profile2 -> author_name1 : id2 : paper1
    # remove id1, id2 for evaluation
    # we have author name - papers, ids - papers. common author names from first map. check one profile's papers subset to other. 
    # if yes, remove corresponding ids from author_to_ids map
     
    


    #evaluation using accuracy, precision, recall
    matching_pairs = []
    non_matching_pairs = []
    cluster_same_group_pairs = []
    clsuter_different_group_pairs = []

    author_ids_list = author_to_ids.values()
    for value in author_ids_list:
        matching_pairs.extend(get_pairs(value))

    authors_ids_indices = list(range(len(list(author_ids_list))))
    author_ids_indices_pairs = get_pairs(authors_ids_indices)
    for pair in author_ids_indices_pairs:
#         print(pair[0])
        non_matching_pairs.extend(get_pairs_from_two_lists(list(author_ids_list)[pair[0]],list(author_ids_list)[pair[1]]))
    
    cluster_ids_list = cluster_to_ids.values()

    for value in cluster_ids_list:
        cluster_same_group_pairs.extend(get_pairs(value))

    clusters_indices = list(range(len(list(cluster_ids_list))))
    cluster_ids_indices_pairs = get_pairs(clusters_indices)
    for pair in cluster_ids_indices_pairs:
#         print(pair[0])
        clsuter_different_group_pairs.extend(get_pairs_from_two_lists((list(cluster_ids_list))[pair[0]],(list(cluster_ids_list))[pair[1]]))

   
    for pair in cluster_same_group_pairs:
        if pair in matching_pairs:
            TP+=1
        elif pair in non_matching_pairs:
            FP+=1
    for pair in clsuter_different_group_pairs:
        if pair in matching_pairs:
            FN+=1
        elif pair in non_matching_pairs:
            TN+=1
    




    

S = TP+FP+TN+FN


# accuracy = (TP+TN)/S
# print("accuracy : ",accuracy)
# pairwise_precision = TP/(TP+FP)
# print("pairwise_precision : ",pairwise_precision)
# pairwise_recall = TP/(TP+FN)
# print("pairwise_recall : ",pairwise_recall)
# pairwise_f1 = (2*pairwise_precision*pairwise_recall)/(pairwise_recall+pairwise_precision)
# print("pairwise_f1 : ",pairwise_f1)
# ler = FP/(TP+FP)
# print("pairwise lumping error rate : ",ler)
# ser = FN/(TN+FN)
# print("pairwise splitting error rate : ",ser)
# er = (FP+FN)/S
# print("pairwise error rate : ",er)


    
print("total clusters: ", str(len(clusters_data)))
print("total splitting: ", str(total_splits))
print("total lumping: ", str(total_lumps))
print("total splitting blocks: ", str(total_splitting_blocks))
print("total lumping blocks: ", str(total_lumping_blocks))
print("lumping_based_on_name: ", str(lumping_based_on_name))
print("splitting_based_on_name: ", str(splitting_based_on_name))
print("authors_per_block_avg: ", str(int(authors_per_block_avg/len(clusters_data))))
print("authors_per_block_max: ", str(authors_per_block_max))
print("authors per block min: ", str(authors_per_block_min))
print("author names found in google scholar: ", str(authors_found_in_google_scholar))
print("duplicate author profiles found in google scholar: ", str(duplicate_author_profiles_on_gs))
print("TP: ", str(TP))
print("FP: ", str(FP))
print("FN: ", str(FN))
print("TN: ", str(TN))
# print("accuracy: ", str())


with open("evaluation_results_gs_fini.txt", "w+") as f:
    f.write("total clusters: "+str(len(clusters_data))+"\n")
    f.write("total splitting: "+str(total_splits)+"\n")
    f.write("total lumping: "+str(total_lumps)+"\n")
    f.write("total splitting blocks: "+str(total_splitting_blocks)+"\n")
    f.write("total lumping blocks: "+str(total_lumping_blocks )+"\n")
    f.write("lumping_based_on_name: "+str(lumping_based_on_name)+"\n")
    f.write("splitting_based_on_name: "+str(splitting_based_on_name)+"\n")
    f.write("authors_per_block_avg: "+str(int(authors_per_block_avg/len(clusters_data)))+"\n")
    f.write("authors_per_block_max: "+str(authors_per_block_max)+"\n")
    f.write("authors per block min: "+str(authors_per_block_min)+"\n")
    f.write("author names found in google scholar: "+str(authors_found_in_google_scholar)+"\n")
    f.write("duplicate author profiles found in google scholar: "+str(duplicate_author_profiles_on_gs)+"\n")
    f.write("TP: "+str(TP)+"\n")
    f.write("FP: "+str(FP)+"\n")
    f.write("FN: "+str(FN)+"\n")
    f.write("TN: "+str(TN)+"\n")
#     f.write("Precision: "+pairwise_precision+"\n")
#     f.write("Recall: "+pairwise_recall+"\n")
#     f.write("Accuracy: "+accuracy+"\n")
#     f.write("PLER: "+ler+"\n")
#     f.write("PSER: "+ser+"\n")
#     f.write("PER: "+er+"\n")
    
    


        
#started at 12:50





































# import sqlite3
# import json
# import ast 
# import sys

# cnx = sqlite3.connect('test3.db')
# cursor = cnx.cursor()
# db = sys.argv[1]
# if db == "gs":
#     query = 'select * from google_scholar where fullname=\'{0}\''
# else:
#     query = 'select * from bhl where fullname=\'{0}\''

# # query2 = 'select * from bhl'
# # cursor.execute(query2)
# # print(cursor.fetchall())

# with open("../clusters_all.txt", 'r', encoding="ISO-8859-1") as f:
#     clusters = f.readlines()

# # print(type(clusters))
# clusters = clusters[0].split('|')
# bad_clusters = 0
# bad_cluster_list = []
# actual_cluster_list = []
# ids_found_in_gs = 0
# splitting = 0
# lumping = 0
# splitting_authors = []
# lumping_authors = []

# for cluster in clusters:
#     new_query = ""
#     try:
#         cluster_list = cluster.split(':')
#         name = cluster_list[0]
#         name = name.strip()
#         name = name.replace('\'','\'\'')
# #         name = (name.encode("ascii", "ignore")).decode("utf-8")
#         new_query = query.format(name)

#         cursor.execute(new_query)
#         result = cursor.fetchall()
#         if len(result) > 0:
#             ids_found_in_gs+=1
#             if db == "gs":
#                 with open('google_scholar_authors.txt', 'a+') as f:
#     #             with open('bhl_authors.txt', 'a+') as f:
#                     f.write(name)
#                     f.write('\n')
#             else:
#                 with open('bhl_authors.txt', 'a+') as f:
#                     f.write(name)
#                     f.write('\n')
        
#             # print(result)
#             # break
#             cluster_author = {}
#             author_cluster = {}
#             for res in result:
#                 author_cluster[res[0]] = set()
#                 cluster_groups = ast.literal_eval(cluster_list[2])
#                 gold_standard_ids = res[2].split(',')
#                 i=0
#                 for cluster_group in cluster_groups:
#                     if i not in cluster_author:
#                         cluster_author[i] = set()
#                     cluster_group_ids = cluster_group.split(';')
#                     for id in gold_standard_ids:
#                         if id in cluster_group_ids:
#                             author_cluster[res[0]].add(i) #add cluster group id to author map
#                             cluster_author[i].add(res[0])
#                     i+=1
        
#             for key,value in cluster_author.items():
#                 if len(value) > 1:
#                     lumping+=1
#                     # lumping_authors.append()
#             for key,value in author_cluster.items():
#                 if len(value) > 1:
#                     splitting+=1
        
#         # if int(cluster_list[3]) > 1:
#         #     if len(result) > 0:
#         #         print(result)
#         #         db_ids = result[0][0].split(',')
#         #         cluster_groups = ast.literal_eval(cluster_list[2])
                
#         #         check = {}
#         #         i=0
#         #         for cluster_group in cluster_groups:
#         #             cluster_group_ids = cluster_group.split(';')
#         #             for db_id in db_ids:
#         #                 if db_id in cluster_group_ids:
#         #                     check[i] = 1
#         #             i+=1
#         #         if(len(check.keys())> 1):
#         #             bad_clusters+=1
#         #             bad_cluster_list.append(cluster)
#         #             actual_cluster_list.append(result[0][0])

                    
#     except Exception as e:
#         print(e)
#         print(new_query)


# # print("bad_clusters:")
# # print(bad_clusters)
# # print(bad_cluster_list)
# # print(actual_cluster_list)
# # print("accuracy", str((len(clusters)-bad_clusters)/len(clusters)))
# # print("total results found in gs", ids_found_in_gs)

# print("splitting clusters")
# print(splitting)
# print("lumping clusters")
# print(lumping)
# print("total clusters")
# print(len(clusters))

# if db=="gs":
#     print("total results found in gs", ids_found_in_gs)
# else:
#     print("total results found in bhl", ids_found_in_gs)
# # print("total results found in gs", ids_found_in_gs)

                

