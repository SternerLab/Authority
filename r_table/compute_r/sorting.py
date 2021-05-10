import json
import bisect
import timeit


def monotonic_sort(_list):
    print("monotonic sort")
    pre_sorted_list = sorted(_list)
    print(pre_sorted_list)
    adj_list = {}
    for value in pre_sorted_list:
        adj_list[value] = []
    
    adj_list = generate_directed_graph(pre_sorted_list, adj_list)
#     return construct_matrix(adj_list, pre_sorted_list)
    return construct_matrix(adj_list, _list)
    
    # print(adj_list)
    # list_ = level_order(adj_list)
    # print(len(list_))
    # return list_
    # print(adj_list)
#     create_lists(adj_list)
    # list_ = BFS2(adj_list)
    # sorted_list = sorted(list_, key=len, reverse=True)
    # final_list = [sorted_list[0]]
    # # print(sorted_list[0])
    # for i in range(1, len(sorted_list)-1):
    #     if(len(sorted_list[i]) != len(sorted_list[i+1]) ):
    #         break
    #     final_list.extend([sorted_list[i]])
    #     # print(sorted_list[i])
    # print((final_list[3]))
    # return final_list
    # return []

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

            


def level_order(adj_list):
    queue = []
    result = []
    queue.append("[1, 0, 0, 0]")
    visited = {}
    for adj in adj_list.keys():
        visited[adj] = False
    visited["[1, 0, 0, 0]"] = True
    # print(adj_list["[1, 0, 0, 0]"])
    while(len(queue) > 0):
        key = queue.pop(0)
        result.append(key)
        for item in adj_list[key]:
            if visited[item] is False:
                queue.append(item)
                visited[item] = True
    return result


def topological_sort(adj_list):
    visited = {}
    stack = []
    list_ = []
    for adj in adj_list.keys():
        visited[adj] = False
    for adj in adj_list.keys():
        if visited[adj] == False:
            topological_sort_util(adj_list, visited, stack, adj)

    while(len(stack) > 0):
        list_.append(stack.pop())
    
    return list_


def topological_sort_util(adj_list, visited, stack, key):
    visited[key] = True
    for item in adj_list[key]:
        if visited[item] is False:
            topological_sort_util(adj_list, visited, stack, item)
    stack.append(key)    


# def create_lists(_list):
#     compatible_lists = []
#     pre_sorted_list = sorted(_list)
#     for value in _list:
#         compatible_lists.append([value])
#     for value in _list:
#         for li in compatible_lists:

#     print(compatible_lists)
        
        

        



# def insert_if_compatible(val1, val2, adj_list):
#     list_val1 = [i for i in adj_list[val1]]
#     for list_ in list_val1:
#         index = bisect.bisect_left(list_, val2)
#         n = len(list_)
#         if index == 0:
#             comparator = compare(val2, list_[index])
#             if comparator < 0:
#                 bisect.insort(list_, val2)
#             else:
#                 new_list = list_[0:index]
#                 bisect.insort(new_list, val2)
#                 adj_list[val1].extend(new_list)
#         elif index == n:
#             comparator = compare(val2, list_[index-1])
#             if comparator > 0:
#                 bisect.insort(list_, val2)
#             else:
#                 new_list = list_[0:index]
#                 bisect.insort(new_list, val2)
#                 adj_list[val1].extend(new_list)
#         else:
#             left_c = compare(val2, list_[index-1])
#             right_c = compare(val2, list_[index])
#             if left_c > 0 and right_c < 0:
#                 bisect.insort(list_, val2)
#             else:
#                 new_list = list_[0:index]
#                 bisect.insort(new_list, val2)
#                 adj_list[val1].extend(new_list)


def generate_directed_graph(pre_sorted_list, adj_list):
    for i in range(0, len(pre_sorted_list)):
        for j in range(i+1, len(pre_sorted_list)):
#             insert_if_compatible(pre_sorted_list[i], pre_sorted_list[j], adj_list)
#     return adj_list 
            comparator = compare(pre_sorted_list[i], pre_sorted_list[j])
            if comparator > 0: #implies pre_sorted_list[i] > pre_sorted_list[j]
#                 bisect.insort(adj_list[pre_sorted_list[j]], pre_sorted_list[i])
                insert_if_compatible(adj_list[pre_sorted_list[j]], pre_sorted_list[i])
            elif comparator < 0: #implies pre_sorted_list[i] < pre_sorted_list[j]
#                 bisect.insort(adj_list[pre_sorted_list[i]], pre_sorted_list[j])
                # if not compatible(pre_sorted_list[j], adj_list[pre_sorted_list[i]]):
                #     adj_list[pre_sorted_list[i]].append(pre_sorted_list[j])
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
    # elif index == 0:
    #     list_.pop(0)
    #     list_.append(val2)



def compatible(val2, list_):
    print(val2)
    print(list_)

    index = bisect.bisect_left(list_, val2)
    print(index)
    n = len(list_)
    if n==0:
        return False
    if index == 0:
        comparator = compare(val2, list_[index])
        if comparator < 0:
            return True
        else:
            return False
    elif index == n:
        comparator = compare(val2, list_[index-1])
        if comparator > 0:
            return True
        else:
            return False
    else:
        left_c = compare(val2, list_[index-1])
        right_c = compare(val2, list_[index])
        if left_c > 0 and right_c < 0:
            return True
        else:
            return False


def insert_pos(list_, val2):
    # if compare(val2, list_[0]) < 0:
    #     return 0
    for i in range(len(list_)):
        if compare(val2, list_[i]) > 0:
            return i, False
        if compare(val2, list_[i]) < 0:
            return i, True
    # if compare(val2, list_[len(list_)-1]) > 0:
    #     return len(list_)-1
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


def BFS2(adj_list):
    visited = {}
    final_list = []
    
    node_start_list = []
    for key, value in adj_list.items():
        node_start_list.extend(value)

    print(len(set(node_start_list)))
    for key in adj_list.keys():
#         node_list[key] = [key]
        if key not in node_start_list:
            print(key)
            visited[key] = 1
            final_list = BFSUtil2(key, adj_list, [key], visited, final_list)
            visited.pop(key)
    return final_list
    # print(final_list)

    
def BFSUtil2(key, adj_list, node_list, visited, final_list):
    # print(adj_list[key])
    if(len(adj_list[key]) == 0):
        # print("new list",node_list)
        temp2 = [i for i in node_list]
        final_list.append(temp2)
        # print(final_list)
        return final_list
    for val in adj_list[key]:
        if val not in visited:
            temp = [i for i in node_list]
            temp.append(val)
            visited[val] = 1
            final_list = BFSUtil2(val, adj_list, temp, visited, final_list)
            # print("after",final_list)
            temp.remove(val)
            visited.pop(val)
    return final_list
    
    
    
def BFS(adj_list):
    final_list = []
    first_key = list(adj_list.keys())[0]
    visited = {}
    visited[first_key] = 1
    BFSUtil(first_key, adj_list, [], final_list, visited)
    print(final_list)
    final = sorted(final_list, key=len, reverse=True)[0]
    # print(adj_list["[9, 1, 0, 0]"])
    return final


def BFSUtil(key, adj_list, cur_list, final_list, visited):
    import copy
    if len(adj_list[key])==0:
        temp_list = copy.deepcopy(cur_list)
        temp_list.append(key)
        final_list.append(temp_list)
#         print(final_list)
    else:
        temp_list = copy.deepcopy(cur_list)
        temp_list.append(key)
        for value in adj_list[key]:
#             if value not in visited:
            visited[value] = 1
            BFSUtil(value, adj_list, temp_list, final_list, visited)


# r_xa = {}
# with open('r_xa_1.json', 'r') as f:
#     r_xa = json.load(f)
# # r_xa = {}
# # r_xa["[1, 1, 0, 0]"] = 1
# # r_xa["[1, 1, 0, 1]"] = 1
# # r_xa["[2, 1, 0, 1]"] = 1
# # r_xa["[1, 1, 0, 2]"] = 1
# # r_xa["[2, 1, 0, 2]"] = 1
# # r_xa["[1, 0, 2, 1]"] = 1
# # r_xa["[1, 0, 2, 2]"] = 1

# # r_xa["[1,1,0,0]"] = 1

# # print(sorted(list(r_xa.keys())[0:10]))
# start = timeit.default_timer()
# sorted_r_xa_keys = monotonic_sort(list(r_xa.keys()))
# print(sorted_r_xa_keys)
# # print(compare("[9, 1, 0, 0]", "[13, 1, 0, 0]"))
# # create_lists(r_xa.keys())
# stop = timeit.default_timer()

# print('Time: ', stop - start)  