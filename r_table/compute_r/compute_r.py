import json

def compute_r_x1():
    #x1 = 0,1,2,3
    r_x1 = {}
    total_m = 0
    total_nm = 0
    for key in x1_m.keys():
        total_m += x1_m[key]
    for key in x1_nm.keys():
        total_nm += x1_nm[key]
    
    for key in set(list(x1_m.keys())+(list(x1_nm.keys()))):
        r_x1[key] = (x1_m[key] / total_m)/(x1_nm[key]/ total_nm)
    # total_m = x1_m[0]+x1_m[1]+x1_m[2]+x1_m[3]
    # total_nm = x1_nm[0]+x1_nm[1]+x1_nm[2]+x1_nm[3]
    
    # r_x1[0] = (x1_m[0] / total_m)/(x1_nm[0] / total_nm)
    # r_x1[1] = (x1_m[1] / total_m)/(x1_nm[1] / total_nm)
    # r_x1[2] = (x1_m[2] / total_m)/(x1_nm[2] / total_nm)
    # r_x1[3] = (x1_m[3] / total_m)/(x1_nm[3] / total_nm)
    
    with open('r_x1.json', 'w') as f:
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
    
    for key in set(list(x2_m.keys())+(list(x2_nm.keys()))):
        r_x2[key] = (x2_m[key] / total_m)/(x2_nm[key]/ total_nm)
    
    with open('r_x2.json', 'w') as f:
        json.dump(r_x2, f)

def compute_r_xa():
    m_keys = xa_m.keys()
    nm_keys = xa_nm.keys()
    intersection = list(set(m_keys) & set(nm_keys))
    total_m = 0
    total_nm = 0
    r_xa = {}
    for key in intersection:
        total_m += xa_m[key]
        total_nm += xa_nm[key]
    # print(sorted(intersection, key=len))
    for key in  intersection:#sorted(intersection, key=len): #sort keys in r_xa. This is required when estimating r(xa) using quadratic programming.
        r_xa[key] = (xa_m[key] / total_m)/(xa_nm[key] / total_nm)
    
    with open('r_xa.json', 'w') as f:
        json.dump(r_xa, f)


with open('x1_m.json') as json_file: 
    x1_m = json.load(json_file) 
with open('x1_nm.json') as json_file: 
    x1_nm = json.load(json_file) 
with open('x2_m.json') as json_file: 
    x2_m = json.load(json_file) 
with open('xa_m.json') as json_file: 
    xa_m = json.load(json_file) 
with open('xa_nm.json') as json_file: 
    xa_nm = json.load(json_file) 
with open('x2_nm.json') as json_file: 
    x2_nm = json.load(json_file) 

compute_r_xa()
compute_r_x1()
compute_r_x2()