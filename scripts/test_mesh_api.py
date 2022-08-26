import skr_web_api
import json
from rich.pretty import pprint

def run():
    print('Imported!')
    with open('umls_credentials.json', 'r') as infile:
        credentials = json.load(infile)
        pprint(credentials) # handy for leaking your personal info
        sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
        # sub.init_generic_batch('semrep', '-D')
        sub.init_generic_batch('metamap', '--XML -E')
        sub.set_batch_file('USERINPUT', 'A spinal tap was performed and oligoclonal bands were detected in the cerebrospinal fluid.\n')
        response = sub.submit()
        print(response.status_code)
        print(response)
        print(response.content)

