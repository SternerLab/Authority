import json
import sorting as sorting
import bisect
from numpy import array


results_folder = 'results'
def compute_r_x1():
    r_x1 = {}
    total_m = 0
    total_nm = 0
    for key in x1_m.keys():
        total_m += x1_m[key]
    for key in x1_nm.keys():
        total_nm += x1_nm[key]
    
    for key in list(set(x1_m.keys()) & set(x1_nm.keys())):
        r_x1[key] = (x1_m[key] / total_m)/(x1_nm[key]/ total_nm)
    
    with open(results_folder+'/r_x1_3k_10k.json', 'w') as f:
        json.dump(r_x1, f)


def compute_r_x2():
    r_x2 = {}
    total_m = 0
    total_nm = 0
    for key in x2_m.keys():
        total_m += x2_m[key]
    for key in x2_nm.keys():
        total_nm += x2_nm[key]
    
    for key in list(set(x2_m.keys()) & set(x2_nm.keys())):
        r_x2[key] = (x2_m[key] / total_m)/(x2_nm[key]/ total_nm)
    
    with open(results_folder+'/r_x2_3k_10k.json', 'w') as f:
        json.dump(r_x2, f)
        
def compute_r_x(jsondata_m, jsondata_nm, filename):
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

    for key in  intersection:
        r_xa[key] = (xa_m[key] / total_m)/(xa_nm[key] / total_nm)
    
    with open(results_folder+'/r_xa.json', 'w') as f:
        json.dump(r_xa, f)

    print(len(r_xa.keys()))


def sort_r_xa():
    return sorting.monotonic_sort(r_xa.keys())


with open(results_folder+'/x1_m_3k_10k.json') as json_file: 
    x1_m = json.load(json_file) 
with open(results_folder+'/x1_nm_3k_10k.json') as json_file: 
    x1_nm = json.load(json_file) 
with open(results_folder+'/x2_m_3k_10k.json') as json_file: 
    x2_m = json.load(json_file) 
with open(results_folder+'/xa_m.json') as json_file: 
    xa_m = json.load(json_file) 
with open(results_folder+'/xa_nm_184000000.json') as json_file: 
    xa_nm = json.load(json_file) 
with open(results_folder+'/x2_nm_3k_10k.json') as json_file: 
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
    
with open(results_folder+'/x3_nm_184000000.json') as json_file: 
    x3_nm = json.load(json_file) 
with open(results_folder+'/x4_nm_184000000.json') as json_file: 
    x4_nm = json.load(json_file) 
with open(results_folder+'/x5_nm_184000000.json') as json_file: 
    x5_nm = json.load(json_file) 
with open(results_folder+'/x6_nm_184000000.json') as json_file: 
    x6_nm = json.load(json_file) 
with open(results_folder+'/x7_nm_184000000.json') as json_file: 
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

        
