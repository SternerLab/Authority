import json
import bisect
import timeit


def monotonic_sort(_list):
    print("monotonic sort")
    pre_sorted_list = sorted(_list)
    # print(pre_sorted_list)
    adj_list = {}
    for value in pre_sorted_list:
        adj_list[value] = []

    adj_list = generate_directed_graph(pre_sorted_list, adj_list)
    return construct_matrix(adj_list, _list)


def construct_matrix(adj_list, pre_sorted_list):
    n = len(pre_sorted_list)
    final_mat = []
    for key in adj_list:
        mat = [0]*n
        index = list(pre_sorted_list).index(key)
        mat[index] = 1
        for val in adj_list[key]:
            index = list(pre_sorted_list).index(val)
            temp = [i for i in mat]
            temp[index] = -1
            final_mat.append(temp)
        # break
    # print(final_mat)
    return final_mat


def generate_directed_graph(pre_sorted_list, adj_list):
    for i in range(0, len(pre_sorted_list)):
        for j in range(i+1, len(pre_sorted_list)):
            comparator = compare(pre_sorted_list[i], pre_sorted_list[j])
            if comparator > 0: #implies pre_sorted_list[i] > pre_sorted_list[j]
                insert_if_compatible(adj_list[pre_sorted_list[j]], pre_sorted_list[i])
            elif comparator < 0: #implies pre_sorted_list[i] < pre_sorted_list[j]
                insert_if_compatible(adj_list[pre_sorted_list[i]], pre_sorted_list[j])
            # else: #implies they are not Comparable
    return adj_list


def insert_if_compatible(list_, val2):
    index, replace_flag = insert_pos(list_, val2)
    if index == -1:
        list_.append(val2)
    elif replace_flag == True:
        list_.pop(index)
        list_.append(val2)


def insert_pos(list_, val2):
    for i in range(len(list_)):
        if compare(val2, list_[i]) > 0:
            return i, False
        if compare(val2, list_[i]) < 0:
            return i, True
    return -1, True


def compare(str_x, str_y):
    # print("str", str_x, str_y)
    x = json.loads(str_x) #converst string representation of list to list
    y = json.loads(str_y)
    x_less_than_y_count = 0
    x_greater_than_y_count = 0
    for i in range(0, len(x)):
        if(x[i] <= y[i]):
            x_less_than_y_count+=1
        if(x[i] >= y[i]):
            x_greater_than_y_count+=1
    if x_less_than_y_count == len(x):
        return -1
    elif x_greater_than_y_count == len(x):
        return 1
    else:
        return 0
