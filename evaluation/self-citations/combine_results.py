import glob
import os
import json

# res = {}
# for filename in glob.glob('*.txt'):
#     with open(os.path.join(os.getcwd(), filename), 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             values = line.split(": ")
#             if(len(values) > 1):
#                 key = values[0]
#                 value = int(values[1].strip())
#                 if key not in res:
#                     res[key] = 0
#                 if key == 'total clusters':
#                     res[key] = value
#                 else:
#                     res[key]=res[key]+value


# with open(os.path.join(os.getcwd(), 'final_eval_results_self.txt'), 'w+') as f:
#     f.write(json.dumps(res))

res = {}
for filename in glob.glob('*aini*.txt'):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        lines = f.readlines()
        for line in lines:
            values = line.split(": ")
            if(len(values) > 1):
                key = values[0]
                value = int(values[1].strip())
                if key not in res:
                    res[key] = 0
                if key == 'total clusters':
                    res[key] = value
                else:
                    res[key]=res[key]+value


with open(os.path.join(os.getcwd(), 'final_eval_results_self_aini.txt'), 'w+') as f:
    f.write(json.dumps(res))

res = {}
for filename in glob.glob('*fini*.txt'):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        lines = f.readlines()
        for line in lines:
            values = line.split(": ")
            if(len(values) > 1):
                key = values[0]
                value = int(values[1].strip())
                if key not in res:
                    res[key] = 0
                if key == 'total clusters':
                    res[key] = value
                else:
                    res[key]=res[key]+value


with open(os.path.join(os.getcwd(), 'final_eval_results_self_fini.txt'), 'w+') as f:
    f.write(json.dumps(res))
