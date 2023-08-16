import skr_web_api
import json
from rich.pretty import pprint
from rich import print

def run():
    print('Imported!')
    with open('umls_credentials.json', 'r') as infile:
        credentials = json.load(infile)
        pprint(credentials) # handy for leaking your personal info
        sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
        sub.init_generic_batch('semrep', '-D')
        sub.set_batch_file('doc.txt')
        response = sub.submit()
        print(response.status_code)
        print(response)
        print(response.content.decode('utf-8'))

