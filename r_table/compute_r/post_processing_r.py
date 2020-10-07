import json
import sorting_util as sorting_util
import bisect


def get_preceeding_profile(key, _list):
    index = bisect.bisect_left(_list, key) #returns the index at which the key can be inserted in the list.
    #check if preceeding profile is monotonically less than given key
    if index > 0:
        val = sorting_util.compare(_list[index-1],key)
        if val != 0:
            return index-1
    return -1 


def get_succeeding_profile(key, _list):
    index = bisect.bisect_left(_list, key) #returns the index at which the key can be inserted in the list.
    #check if preceeding profile is monotonically less than given key
    if index < len(_list)-1:
        val = sorting_util.compare(_list[index+1],key)
        if val != 0:
            return index+1
    return -1 

def interpolate(r_xa_sorted):
    #x3,x4,x5,x6,x8,x9 = 9,1,7,9,12,0
    #x3,x4,x5,x6,x8,x9 = 9,1,7,9,0,1

    #we do not have x8 and x9.
    upper_profile_key = list(r_xa_sorted.keys())[len(r_xa_sorted.keys())-1]
    print(upper_profile_key)
    upper_profile = json.loads(upper_profile_key) #converts string representation of list to list
    print(upper_profile)

    #total possibilities 10*2*8*10 = 1600
    for x3 in range(0,upper_profile[0]):
        for x4 in range(0,upper_profile[1]):
            for x5 in range(0,upper_profile[2]):
                for x6 in range(0,upper_profile[3]):
                    xa = str([x3, x4, x5, x6])
                    print(xa)
                    if xa != "[0,0,0,0]":
                        pa = get_preceeding_profile(xa, list(r_xa_sorted.keys()))
                        sa = get_succeeding_profile(xa, list(r_xa_sorted.keys()))
                        if pa!=-1 and sa!=-1:
                            r_xa_sorted[xa] = (r_xa_sorted[pa] + r_xa_sorted[sa])/2

    return r_xa_sorted


def assign_smoothened_values():
    with open('r_smoothen.txt', 'r') as f:
        lines = f.readlines()
    i = 0
    for key in r_xa_sorted.keys():
        r_xa_sorted[key] = lines[i].strip()
        i+=1


with open('r_xa_sorted.json', 'r') as f:
    r_xa_sorted = json.load(f)

assign_smoothened_values()
print(r_xa_sorted)
r_interpolated = interpolate(r_xa_sorted)
print(r_interpolated)

with open('r_final.json', 'w') as f:
    json.dump(r_interpolated, f)