import requests
import urllib.parse

from rich.pretty import pprint

API_URL = 'https://api.crossref.org/works?query.bibliographic={citation}'

def crossref_citation(citation):
    ''' Absolute overkill for tracking down a citation '''
    url = API_URL.format(citation=urllib.parse.quote_plus(citation))
    response = requests.get(url).json()
    pprint(response)
    if response['status'] == 'ok':
        return response['result']
