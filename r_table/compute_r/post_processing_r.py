import json
import sorting as sorting
import bisect

results_folder = 'results'

def get_preceeding_profile(key, _list):
    min_dist = 100
    min_key = -1
    for i in range(0, len(_list)):
        if sorting.compare(key,_list[i]) > 0:
            diff = get_difference(key, _list[i])
            if diff < min_dist:
                # print(key,_list[i],diff)
                min_key = _list[i]

    return min_key


def get_succeeding_profile(key, _list):
    min_dist = 100
    min_key = -1
    for i in range(0, len(_list)):
        if sorting.compare(key,_list[i]) < 0:
            diff = get_difference(key, _list[i])
            if diff < min_dist:
                min_key = _list[i]
    return min_key


def get_difference(key1, key2):
    x = json.loads(key1) #converst string representation of list to list
    y = json.loads(key2)
    diff = 0
    for i in range(0, len(x)):
        diff += abs(x[i] - y[i])
    return diff


def interpolate(r_xa_sorted):
    #x3,x4,x5,x6,x8,x9 = 9,1,7,9,12,0
    #x3,x4,x5,x6,x8,x9 = 9,1,7,9,0,1

    #we do not have x8 and x9.
    # upper_profile_key = list(r_xa_sorted.keys())[len(r_xa_sorted.keys())-1]
    # print(upper_profile_key)
    # upper_profile = json.loads(upper_profile_key) #converts string representation of list to list
    # print(upper_profile)
    # upper_profiles = ["[6, 1, 0, 15]", "[7, 1, 0, 12]"]
#     ['[9, 0, 0, 10]', '[6, 1, 0, 15]', '[9, 1, 0, 8]', '[11, 1, 0, 6]', '[8, 1, 0, 9]', '[7, 1,
# 0, 12]', '[10, 1, 0, 7]', '[14, 1, 0, 5]']
    upper_profiles = get_upper_profiles(list(r_xa_sorted.keys()))

    print(upper_profiles)
    with open(results_folder+'/upper_profiles.txt', 'w') as f:
        f.write(str(upper_profiles))
    x3_max, x4_max, x5_max, x6_max, x7_max = 0,0,0,0,0
    for profile in upper_profiles:
        profile_attributes = json.loads(profile)
        x3_max, x4_max, x5_max, x6_max, x7_max = max(x3_max, profile_attributes[0]), max(x4_max, profile_attributes[1]), max(x5_max, profile_attributes[2]), max(x6_max, profile_attributes[3]), max(x7_max, profile_attributes[4])

    count = 0
    print(x3_max, x4_max, x5_max, x6_max, x7_max)
    for i in range(0, 1):
        #total possibilities
        # upper_profile = json.loads(upper_profiles[i])
        for x3 in range(1, x3_max+1):
            for x4 in range(0, x4_max+1):
                for x5 in range(0, x5_max+1):
                    for x6 in range(0, x6_max+1):
                        for x7 in range(0, x7_max+1):
                            xa = str([x3, x4, x5, x6, x7])
                            print(xa)
                            if xa not in r_xa_sorted:
                                count+=1
                            # if xa != "[0, 0, 0, 0]":
                                pa = get_preceeding_profile(xa, list(r_xa_sorted.keys()))
                                sa = get_succeeding_profile(xa, list(r_xa_sorted.keys()))
                                # print(pa, sa)
                                if pa!=-1 and sa!=-1:
                                    r_xa_sorted[xa] = (r_xa_sorted[pa] + r_xa_sorted[sa])/2
                                    # print(r_xa_sorted[xa])
    print(count)
    return r_xa_sorted


def get_upper_profiles(list_):
    upper_profiles = []
    for i in range(0, len(list_)):
        # index, is_max = max_element(list_[i], upper_profiles)
        # # if list_[i] == "[4, 1, 0, 12]":
        # #     print(list_[i], upper_profiles, index, is_max)
        # if is_max is True and index>-1:
        #     upper_profiles.pop(index)
        #     upper_profiles.append(list_[i])
        # elif index == -1 and is_max is True:
        #     upper_profiles.append(list_[i])
        # if list_[i] == "[4, 1, 0, 12]":
        #     print(list_[i], upper_profiles, index, is_max)
        upper_profiles = insert_if_max(upper_profiles, list_[i])

    return upper_profiles


def insert_if_max(list_, key):
    insert = False
    insert_count = 0
    remove_elements = []

    if len(list_) == 0:
        insert = True
    for i in range(len(list_)):
        compare =  sorting.compare(key, list_[i])
        if compare> 0:
            remove_elements.append(list_[i])
            insert = True
        elif compare == 0:
            insert_count+=1

    temp_list = [i for i in list_]
    for i in range(len(remove_elements)):
        temp_list.remove(remove_elements[i])
    if insert is True or insert_count == len(list_):
        temp_list.append(key)
    return temp_list


def max_element(key, list_):
    for i in range(len(list_)):
        if sorting.compare(key, list_[i]) < 0:
            return i, False
        if sorting.compare(key, list_[i]) > 0:
            return i, True
    return -1, True



def assign_smoothened_values():
    with open(results_folder+'/r_smoothen.txt', 'r') as f:
        lines = f.readlines()
    i = 0
    for key in r_xa_sorted.keys():
        r_xa_sorted[key] = float(lines[i].strip())
        i+=1
    return r_xa_sorted


with open(results_folder+'/r_xa.json', 'r') as f:
    r_xa_sorted = json.load(f)

print("before interpolation:")
print(len(r_xa_sorted.keys()))
r_xa_sorted_smoothen = assign_smoothened_values()
r_interpolated = interpolate(r_xa_sorted_smoothen)
print("after interpolation:")
print(len(r_interpolated.keys()))

# print(r_interpolated)

with open(results_folder+'/r_final_without_interpolation.json', 'w') as f:
    json.dump(r_xa_sorted_smoothen, f)

with open(results_folder+'/r_final.json', 'w') as f:
    json.dump(r_interpolated, f)
# print((r_xa_sorted.keys()))
# print("test")
# print(sorting.compare("[7, 1, 0, 12]", "[6, 1, 0, 15]"))
