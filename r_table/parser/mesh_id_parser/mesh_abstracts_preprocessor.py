import argparse

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="path of output folder to parse and process", required=True)
    args = parser.parse_args()
    zip_file = args.file
    return zip_file




file_name = parse_arguments()
# file_name = "test.txt"

with open(file_name, 'r') as f:
    content = f.readlines()

final_content = ''
for value in content:
    if value.strip() != '':
        id_abstract = value.strip().split('|')
        if id_abstract[1]!=''  and len(id_abstract[1]) < 10000:
            final_content+= value
        elif len(id_abstract[1]) >= 10000:
            id_abstract[1] = id_abstract[1][:9999]
            final_content+= id_abstract[0] + "|" + id_abstract[1]

with open(file_name, 'w') as f:
    f.write(final_content)
