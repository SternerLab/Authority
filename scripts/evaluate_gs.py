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

def run():
    cnx = sqlite3.connect('database/jstor-authority.db')

    clusters_data = pd.read_sql_query("SELECT * from clusters_all", cnx)
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
        print(row)

        clusters = ast.literal_eval(row["clusters"])
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
        author_names = row["authors"].strip().split(',')
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
    S = TP+FP+TN+FN

    with open("evaluation_results_gs.txt", "w+") as f:
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
#     f.write("Precision: "+str(TP/(TP+FP))+"\n")
#     f.write("Recall: "+str(TP/(TP+FN))+"\n")
#     f.write("Accuracy: "+str((TP+TN)/S)+"\n")
#     f.write("PLER: "+str(FP/(TP+FP))+"\n")
#     f.write("PSER: "+str(FN /(TN + FN ))+"\n")
#     f.write("PER: "+str((FP + FN )/S)+"\n")





