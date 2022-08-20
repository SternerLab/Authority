import sqlite3
import json
import pandas as pd
import ast
import sys


import itertools

  

def get_pairs(list_):
    return itertools.combinations(list_, 2)


def get_pairs_from_two_lists(lista, listb):
    return list(itertools.product(lista, listb))

cnx = sqlite3.connect('../../database/jstor-authority-old-for-plots-2.db')
cursor = cnx.cursor()

search_self_query = "select * from self_citations where ids like \'%,%\' and lower(full_name) like '"
query = "select distinct id as clusters, fullname as authors, first_initial, middle_initial, last_name from articles"
old_data = pd.read_sql_query(query,cnx)
data = old_data
data['clusters'] = data.groupby(["first_initial", "middle_initial", "last_name"])['clusters'].transform(lambda x : ';'.join(x))
data['authors'] = data.groupby(["first_initial", "middle_initial", "last_name"])['authors'].transform(lambda x : ','.join(x))
data = data.drop_duplicates()
clusters_data = data


total_clusters = 0
total_splits = 0
total_splitting_blocks = 0
authors_found_in_self_citations = 0
TP =0
TN = 0
FP = 0
FN = 0
index_from = sys.argv[1]
index_to = sys.argv[2]
tot = 0

for index,row in clusters_data[int(index_from):int(index_to)].iterrows():
    #we consider only splitting scenario. self citation data has pair(s) of articles attributed to an author. 
    #we check if each pair belong to a same cluster.
    clusters = row["clusters"].split(',')
    tot+=1
    i = 0
    cluster_to_author_map = {} 
    author_to_cluster_map = {} 
    cluster_to_ids = {}
    author_to_ids = {}
    for cluster in clusters:
        cluster_to_ids[i] = cluster.split(';')
        i+=1
    
    author_names = list(set(row["authors"].strip().split(',')))
    j = 0
    for author in author_names:
        auth_query = search_self_query+author.strip().replace('\'', '\'\'')+"'"
        author_selfc_data = pd.read_sql_query(auth_query,cnx)
        for index, row in author_selfc_data.iterrows():
            author_to_ids[j] = row["ids"].split(',')
            j+=1
        if not author_selfc_data.empty:
            authors_found_in_self_citations+=1

    # print(cluster_to_ids)
    # print(author_to_ids)
    # print("...")

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
                        cluster_to_author_map[i].add(j)
                    else:
                        cluster_to_author_map[i] = set()
                        cluster_to_author_map[i].add(j)
                    if j in author_to_cluster_map:
                        author_to_cluster_map[j].add(i)
                    else:
                        author_to_cluster_map[j] = set()
                        author_to_cluster_map[j].add(i)
            j+=1
        i+=1
    
#     print(author_to_cluster_map)
#     print(cluster_to_author_map)
#     print("...")

    #compute splits
    for val in author_to_cluster_map:
        if len(author_to_cluster_map[val]) > 1:
            total_splits+=1

    #compute splits per block
    for val in author_to_cluster_map:
        if len(author_to_cluster_map[val]) > 1:
            total_splitting_blocks+=1
            break

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
    with open("evaluation_results_aini"+index_from+"_"+index_to+".txt", "w+") as f:
        f.write("total clusters: "+str(len(clusters_data))+"\n")
        f.write("total splitting: "+str(total_splits)+"\n")
        f.write("total splitting blocks: "+str(total_splitting_blocks)+"\n")
        f.write("author names found in self citations: "+str(authors_found_in_self_citations)+"\n")
        f.write("TP: "+str(TP)+"\n")
        f.write("FP: "+str(FP)+"\n")
        f.write("FN: "+ str(FN)+"\n")
        f.write("TN: "+ str(TN)+"\n")
        f.write("total processed: "+ str(tot)+"\n")
        
    
print("total clusters: ", str(len(clusters_data)))
print("total splitting: ", str(total_splits))
print("total splitting blocks: ", str(total_splitting_blocks))
print("author names found in self citations: ", str(authors_found_in_self_citations))

with open("evaluation_results_aini"+index_from+"_"+index_to+".txt", "w+") as f:
    f.write("total clusters: "+str(len(clusters_data))+"\n")
    f.write("total splitting: "+str(total_splits)+"\n")
    f.write("total splitting blocks: "+str(total_splitting_blocks)+"\n")
    f.write("author names found in self citations: "+str(authors_found_in_self_citations)+"\n")
    f.write("TP: "+str(TP)+"\n")
    f.write("FP: "+str(FP)+"\n")
    f.write("FN: "+ str(FN)+"\n")
    f.write("TN: "+ str(TN)+"\n")
    f.write("total processed: "+ str(tot)+"\n")
    f.write("done")
