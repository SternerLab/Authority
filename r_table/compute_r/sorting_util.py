import json


def monotonic_sort(_list):
    pre_sorted_list = sorted(_list)
    adj_list = {}
    for value in pre_sorted_list:
        adj_list[value] = []
    
    adj_list = generate_directed_graph(pre_sorted_list, adj_list)
    sorted_list = BFS(adj_list)
    return sorted_list


def generate_directed_graph(pre_sorted_list, adj_list):
    for i in range(0,len(pre_sorted_list)):
        for j in range(i+1, len(pre_sorted_list)):
            comparator = compare(pre_sorted_list[i], pre_sorted_list[j])
            if comparator > 0: #implies pre_sorted_list[i] > pre_sorted_list[j]
                adj_list[pre_sorted_list[j]].append(pre_sorted_list[i])
            elif comparator < 0: #implies pre_sorted_list[i] < pre_sorted_list[j]
                adj_list[pre_sorted_list[i]].append(pre_sorted_list[j])
            # else: #implies they are not Comparable
    return adj_list


def compare(str_x, str_y):
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


def BFS(adj_list):
    final_list = []
    first_key = list(adj_list.keys())[0]
    BFSUtil(first_key, adj_list, [], final_list)
    # print(final_list)
    final = sorted(final_list, key=len, reverse=True)[0]
    # print(adj_list["[9, 1, 0, 0]"])
    return final


def BFSUtil(key, adj_list, cur_list, final_list):
    import copy
    if len(adj_list[key])==0:
        temp_list = copy.deepcopy(cur_list)
        temp_list.append(key)
        final_list.append(temp_list)
        # print(final_list)
    else:
        temp_list = copy.deepcopy(cur_list)
        temp_list.append(key)
        for value in adj_list[key]:
            BFSUtil(value, adj_list, temp_list, final_list)


# r_xa = {}
# with open('r_xa.json', 'r') as f:
#     r_xa = json.load(f)

# sorted_r_xa_keys = monotonic_sort(r_xa.keys())
# print(sorted_r_xa_keys)
# print(compare("[9, 1, 0, 0]", "[13, 1, 0, 0]"))