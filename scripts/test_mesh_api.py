import skr_web_api
import json

def run():
    print('Imported!')
    with open('umls_credentials.json', 'r') as infile:
        credentials = json.read(infile)
        sub = skr_web_api.Submission(credentials['email'], credentials['api_key'])
        sub.init_generic_batch('semrep', '-D')
        sub.set_batch_file('test')
        response = sub.submit()
        print(response)
        print(response.content)

