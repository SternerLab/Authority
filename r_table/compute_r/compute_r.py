import json
import sorting as sorting
import bisect
from numpy import array


results_folder = 'results'
def compute_r_x1():
    #x1 = 0,1,2,3
    r_x1 = {}
    total_m = 0
    total_nm = 0
    for key in x1_m.keys():
        total_m += x1_m[key]
    for key in x1_nm.keys():
        total_nm += x1_nm[key]
    
    for key in list(set(x1_m.keys()) & set(x1_nm.keys())):
        r_x1[key] = (x1_m[key] / total_m)/(x1_nm[key]/ total_nm)
    # total_m = x1_m[0]+x1_m[1]+x1_m[2]+x1_m[3]
    # total_nm = x1_nm[0]+x1_nm[1]+x1_nm[2]+x1_nm[3]
    
    # r_x1[0] = (x1_m[0] / total_m)/(x1_nm[0] / total_nm)
    # r_x1[1] = (x1_m[1] / total_m)/(x1_nm[1] / total_nm)
    # r_x1[2] = (x1_m[2] / total_m)/(x1_nm[2] / total_nm)
    # r_x1[3] = (x1_m[3] / total_m)/(x1_nm[3] / total_nm)
    
    with open(results_folder+'/r_x1.json', 'w') as f:
        json.dump(r_x1, f)


def compute_r_x2():
    #x2 = 0,1
    r_x2 = {}
    total_m = 0
    total_nm = 0
    for key in x2_m.keys():
        total_m += x2_m[key]
    for key in x2_nm.keys():
        total_nm += x2_nm[key]
    
    for key in list(set(x2_m.keys()) & set(x2_nm.keys())):
        r_x2[key] = (x2_m[key] / total_m)/(x2_nm[key]/ total_nm)
    
    with open(results_folder+'/r_x2.json', 'w') as f:
        json.dump(r_x2, f)
        
def compute_r_x(jsondata_m, jsondata_nm, filename):
    #x2 = 0,1
    dict_ = {}
    total_m = 0
    total_nm = 0
    for key in jsondata_m.keys():
        total_m += jsondata_m[key]
    for key in jsondata_nm.keys():
        total_nm += jsondata_nm[key]
    
    for key in list(set(jsondata_m.keys()) & set(jsondata_nm.keys())):
        dict_[key] = (jsondata_m[key] / total_m)/(jsondata_nm[key]/ total_nm)
    
    with open(results_folder+'/'+filename, 'w') as f:
        json.dump(dict_, f)


def compute_r_x10():
    #x2 = 0,1
    r_x10 = {}
    total_m = 0
    total_nm = 0
    for key in x10_m.keys():
        total_m += x10_m[key]
    for key in x10_nm.keys():
        total_nm += x10_nm[key]
    
    for key in list(set(x10_m.keys()) & set(x10_nm.keys())):
        r_x10[key] = (x10_m[key] / total_m)/(x10_nm[key]/ total_nm)
    
    with open(results_folder+'/r_x10.json', 'w') as f:
        json.dump(r_x10, f)
        

def compute_r_xa():
    m_keys = xa_m.keys()
    nm_keys = xa_nm.keys()
    intersection = list(set(m_keys) & set(nm_keys))
    total_m = 0
    total_nm = 0
    for key in intersection:
        total_m += xa_m[key]
        total_nm += xa_nm[key]
    # print(sorted(intersection, key=len))
    for key in  intersection:#sorted(intersection, key=len): #sort keys in r_xa. This is required when estimating r(xa) using quadratic programming.
        r_xa[key] = (xa_m[key] / total_m)/(xa_nm[key] / total_nm)
    
    with open(results_folder+'/r_xa.json', 'w') as f:
        json.dump(r_xa, f)

    print(len(r_xa.keys()))


def sort_r_xa():
    return sorting.monotonic_sort(r_xa.keys())


# def quadratic(keys, r_xa):
#     return quadratic_solver.solve(keys, r_xa, xa_m, xa_nm)
def construct_W_matrix(r_xa, xa_m, xa_nm):
    keys = list(r_xa.keys())
    final_mat = []
    i =0
    for key in keys:
        mat = [0]*len(keys)
        w_xa = xa_m[key] + xa_nm[key]
        value = 2*w_xa*w_xa
        mat[i] = value
        i+=1
        final_mat.append(mat)
    return array(final_mat)


def construct_f_matrix(r_xa, xa_m, xa_nm):
    f_t = []
    for key in r_xa.keys():
        w_xa = xa_m[key] + xa_nm[key]
        value = -2*w_xa*w_xa*r_xa[key]
        f_t.append(value)
    return array(f_t).reshape(len(f_t),1)    





with open(results_folder+'/x1_m.json') as json_file: 
    x1_m = json.load(json_file) 
with open(results_folder+'/x1_nm.json') as json_file: 
    x1_nm = json.load(json_file) 
with open(results_folder+'/x2_m.json') as json_file: 
    x2_m = json.load(json_file) 
with open(results_folder+'/xa_m.json') as json_file: 
    xa_m = json.load(json_file) 
with open(results_folder+'/xa_nm.json') as json_file: 
    xa_nm = json.load(json_file) 
with open(results_folder+'/x2_nm.json') as json_file: 
    x2_nm = json.load(json_file) 
with open(results_folder+'/x10_m.json') as json_file: 
    x10_m = json.load(json_file) 
with open(results_folder+'/x10_nm.json') as json_file: 
    x10_nm = json.load(json_file) 
    
with open(results_folder+'/x3_m.json') as json_file: 
    x3_m = json.load(json_file) 
with open(results_folder+'/x4_m.json') as json_file: 
    x4_m = json.load(json_file) 
with open(results_folder+'/x5_m.json') as json_file: 
    x5_m = json.load(json_file) 
with open(results_folder+'/x6_m.json') as json_file: 
    x6_m = json.load(json_file) 
with open(results_folder+'/x7_m.json') as json_file: 
    x7_m = json.load(json_file) 
    
with open(results_folder+'/x3_nm_45000000.json') as json_file: 
    x3_nm = json.load(json_file) 
with open(results_folder+'/x4_nm_45000000.json') as json_file: 
    x4_nm = json.load(json_file) 
with open(results_folder+'/x5_nm_45000000.json') as json_file: 
    x5_nm = json.load(json_file) 
with open(results_folder+'/x6_nm_45000000.json') as json_file: 
    x6_nm = json.load(json_file) 
with open(results_folder+'/x7_nm_45000000.json') as json_file: 
    x7_nm = json.load(json_file)  

r_xa = {}
compute_r_xa()
compute_r_x1()
compute_r_x2()
compute_r_x10()
compute_r_x(x3_m, x3_nm, 'r_x3.json')
compute_r_x(x4_m, x4_nm, 'r_x4.json')
compute_r_x(x5_m, x5_nm, 'r_x5.json')
compute_r_x(x6_m, x6_nm, 'r_x6.json')
compute_r_x(x7_m, x7_nm, 'r_x7.json')


with open(results_folder+'/r_xa.json') as json_file: 
    r_xa = json.load(json_file) 

A = sort_r_xa()

with open(results_folder+'/A_matrix.txt', 'w') as f:
    for list_ in A:
        li = ""
        for item in list_:
            li += str(item)+" "
        f.writelines(li)
        f.write('\n')

        
# r_xa_sorted_keys = sort_r_xa()
# print("final_list_poset length", len(r_xa_sorted_keys))
# print("final_list_poset 1 length", len(r_xa_sorted_keys[0]))
# print("final_list_poset 2 length", len(r_xa_sorted_keys[1]))

# r_xa_sorted = {}
# for i in range(0, 4):
#     print(r_xa_sorted_keys[i])
    
# upper_profile = []

# for i in range(0, len(r_xa_sorted_keys)):
#     # print(r_xa_sorted_keys[i])
#     for value in r_xa_sorted_keys[i]:
#         # print(value)
#         if i in r_xa_sorted:
#             r_xa_sorted[i][value] = r_xa[value]
#         else:
#             r_xa_sorted[i] = {}
#             r_xa_sorted[i][value] = r_xa[value]
#     # if sorting.compare(upper_profile, value) < 0:
#     upper_profile.append(value)

# print("upper_profile: ", set(upper_profile))

# for i in range(0,10):
#     with open('results/r_xa_sorted_all_'+str(i)+'.json', 'w+') as json_file:
#         json.dump(r_xa_sorted[i], json_file)

# print((r_xa_sorted_keys))

# r_xa_smoothen = smoothen(r_xa_sorted)

# r_xa_interpolated = interpolate(r_xa_smoothen)
# print((r_xa_interpolated))

# r_xa_sorted = {}
# for item in r_xa_sorted_keys:
#     r_xa_sorted[item] = r_xa[item]

# with open('results/r_xa_sorted.json', 'w') as f:
#     json.dump(r_xa_sorted, f)

# A_matrix_for_smoothing = array(sort_r_xa())
# keys = r_xa.keys()

# W_matrix_for_smoothing = construct_W_matrix(r_xa, xa_m, xa_nm)
# f_matrix = construct_f_matrix(r_xa, xa_m, xa_nm)

# b_matrix = array([0]*len(A_matrix_for_smoothing)).reshape(len(A_matrix_for_smoothing), 1)
# Aeq_matrix = [0]*len(r_xa.keys())
# beq_matrix = [0]*1


# print(solve_qp(W_matrix_for_smoothing, f_matrix,A_matrix_for_smoothing, b_matrix))
# print(A_matrix_for_smoothing[0])


