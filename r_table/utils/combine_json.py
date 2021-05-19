import json
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file1",  required=True)
    parser.add_argument("--input-file2",  required=True)
    parser.add_argument("--output-file",  required=True)

    args = parser.parse_args()
    input_file1 = args.input_file1
    input_file2 = args.input_file2
    output_file = args.output_file
    return input_file1, input_file2, output_file


input_file1, input_file2, output_file = parse_arguments()
with open(input_file1) as input_file:
    a = json.load(input_file)

with open(input_file2) as input_file:
    b = json.load(input_file)

with open(output_file, 'w') as f:
    out = dict(list(a.items()) + list(b.items()))
    json.dump(out, f)

print(len(out.keys()))