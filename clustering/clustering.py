from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np
import json
import itertools
import copy
import math

def product(pairs, last_name, first_initial, probabilities):
    c1 = pairs[0].split(';')
    c2 = pairs[1].split(';')
    product = 1
    for i in range(0, len(c1)):
        for j in range(0, len(c2)):
            pij_key = str([c1[i], c2[j], last_name, first_initial])
            pji_key = str([c2[j], c1[i], last_name, first_initial])

            if pij_key in probabilities:
                product = product*((probabilities[pij_key]/(1-probabilities[pij_key]))/(len(c1)*len(c2)))
                # print(pij_key)
                # print(probabilities[pij_key])

            elif pji_key in probabilities:
                product = product*((probabilities[pji_key]/(1-probabilities[pji_key]))/(len(c1)*len(c2)))
                # print(pji_key)
                # print(probabilities[pji_key])
            else:
                print("key doesnt exist")
                print(pij_key)
                print(pji_key)
    return product


def remove_from_clusters(cluster, key):
    cluster.remove(key[0])
    cluster.remove(key[1])


def add_to_clusters(cluster, key):
    keys = key[0] + ';' + key[1]
    cluster.append(keys)


def stopping_condition(clusters, last_name, first_initial, probabilities):
    for i in range(0, len(clusters)):
        for j in range(i+1, len(clusters)):
            c1 = clusters[i].split(';')
            c2 = clusters[j].split(';')
            for k in range(len(c1)):
                for l in range(len(c2)):
                    pij_key = str([c1[k], c2[l], last_name, first_initial])
                    pji_key = str([c2[l], c1[k], last_name, first_initial])
                    if pij_key in probabilities:
                        if probabilities[pij_key] > 0.5:
                            return True

                    elif pji_key in probabilities:
                        if probabilities[pji_key] > 0.5:
                            return True

                    else:
                        print("key doesnt exit")
                        print(pij_key)
                        print(pji_key)
    return False


def obj_product(clusters, initial_clusters, probabilities, last_name, first_initial):
    #clusters = [1;3 , 2]
    #clusters_prev = [1,2,3]
    cluster_groups = {}
    i = 0
    for group in clusters:
        for value in group.split(';'):
            cluster_groups[value]=i
        i+=1

    # product = 1
    log_sum = 0
    pairs = list(itertools.combinations(initial_clusters, 2))
    for pair in pairs:
        i = pair[0]
        j = pair[1]
        pij_key = str([i,j,last_name, first_initial])
        pji_key = str([j,i,last_name, first_initial])
        if pij_key in probabilities:
            probability = probabilities[pij_key]
        elif pji_key in probabilities:
            probability = probabilities[pji_key]
        else:
            print("key doesnt exist")
            print(pij_key)
            print(pji_key)
        if cluster_groups[i] == cluster_groups[j]:
            log_sum+=math.log10(probability)
            # product*=probability
        else:
            # product*=(1-probability)
            log_sum+=math.log10(1-probability)
        # if product < 10**-100:
        #     product*=10**100
        # print(product)
#         print(log_sum)
        # if product == 0:
        #     print(probability)
    return log_sum


def stopping_condition_obj(clusters, clusters_prev, initial_clusters, last_name, first_initial, probabilities):
    if clusters_prev == []:
        return True
    product_cluster = obj_product(clusters, initial_clusters, probabilities, last_name, first_initial)
    product_cluster_prev = obj_product(clusters_prev, initial_clusters, probabilities, last_name, first_initial)
    if product_cluster > product_cluster_prev:
        return True
    return False


def get_clusters(probabilities, last_name, first_initial):
    clusters = []
    clusters_prev = []
    for key in probabilities.keys():
        key_list = key.strip(']').strip('[').split(',')
        clusters.append(key_list[0].strip().replace("\'", ""))
        clusters.append(key_list[1].strip().replace("\'", ""))
    clusters = list(set(clusters))
    initial_clusters = copy.deepcopy(clusters)
    # print("before clustering")
    # print(clusters)

    while(1):
        if stopping_condition_obj(clusters, clusters_prev, initial_clusters, last_name, first_initial, probabilities) == False:
            return clusters_prev
        else:
            clusters_prev = copy.deepcopy(clusters)
            pairs = list(itertools.combinations(clusters, 2))
            max_p = None
            max_p_key = None
            for pair in pairs:
                pair_product = product(pair, last_name, first_initial, probabilities)
                if max_p is None or max_p < pair_product:
                    max_p = pair_product
                    max_p_key = pair
            if max_p_key is not None:
                remove_from_clusters(clusters, max_p_key)
                add_to_clusters(clusters, max_p_key)

    # print("after clustering")
    # print(clusters)
    return clusters


# probabilities = {}
# with open('final_probabilities_authorRickett_H.json', 'r') as f:
#     probabilities = json.load(f)


# get_clusters(probabilities, 'Rickett', 'H')

# prob = {"['1', '2', 'f', 'l']":0.6,"['1', '3', 'f', 'l']":0.7,"['3', '2', 'f', 'l']":0.01}
