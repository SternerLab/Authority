from rich.pretty import pprint
import requests
import json

from ..parse.parse import parse_name, construct_name, remove_stop_words

from .resolver import Resolver

class BiodiversityResolver(Resolver):
    ''' A specialized class for resolving labels for author clusters
        To be specifically used for biodiversity'''
    def __init__(self, client, name):
        self.name  = name
        self.cache = None
        self.collection = client.validation.bhl

    def resolve(self, cluster):
        gid = cluster['group_id']
        name = f'{gid["first_initial"].title()}. {gid["last"].title()}'
        key  = f'{gid["first_initial"].lower()}{gid["last"].lower()}'

        reference_clusters = []
        resolved = 0
        for doc in self.collection.find({'author.key' : key}):
            reference_clusters.append([str(_id) for _id in doc['mongo_ids']])
            resolved += 1
        if resolved > 0:
            print('resolved', resolved)
        return reference_clusters

    def build_cache(self):
        pass

author_search_url = 'https://www.biodiversitylibrary.org/api3?op=AuthorSearch&authorname={author}&apikey={key}&format=json'
metadata_url = 'https://www.biodiversitylibrary.org/api3?op=GetAuthorMetadata&id={idn}&pubs=t&apikey={key}&format=json'


def lookup(author, key=None):
    assert key is not None
    url = author_search_url.format(key=key, author=author)
    response = requests.get(url).json()
    if response['Status'] == 'ok':
        for bhl_author in response['Result']:
            author_id = bhl_author['AuthorID']
            metadata = requests.get(
                metadata_url.format(key=key, idn=author_id)).json()
            if metadata['Status'] == 'ok':
                for result in metadata['Result']:
                    try:
                        yield parse(result)
                    except Exception as e:
                        print(e)


def parse(metadata):
    # pprint(metadata)
    metadata['author_id'] = metadata['AuthorID']
    metadata['author']    = parse_bhl_name(metadata['Name'])
    metadata['titles']    = [remove_stop_words(pub['Title'])
                             for pub in metadata['Publications']]
    return metadata

def parse_bhl_name(bhl_name):
    last, first = bhl_name.split(',')
    data = {'given-names' : first.strip(), 'surname' : last.strip()}
    return parse_name(data, order=0)

''' Example JSON data
{
│   'AuthorID': '275745',
│   'Name': 'Snow, R.',
│   'CreatorUrl': 'https://www.biodiversitylibrary.org/creator/275745'
}
[
│   {
│   │   'AuthorID': '275745',
│   │   'Name': 'Snow, R.',
│   │   'CreatorUrl': 'https://www.biodiversitylibrary.org/creator/275745',
│   │   'CreationDate': '2021/08/22 08:00:40',
│   │   'Publications': [
│   │   │   {
│   │   │   │   'BHLType': 'Part',
│   │   │   │   'FoundIn': 'Metadata',
│   │   │   │   'Volume': '37',
│   │   │   │   'Authors': [{'Name': 'Snow, R.'}],
│   │   │   │   'PartUrl': 'https://www.biodiversitylibrary.org/part/319066',
│   │   │   │   'PartID': '319066',
│   │   │   │   'Genre': 'Article',
│   │   │   │   'Title': 'The conduction of geotropic excitation in roots',
│   │   │   │   'ContainerTitle': 'Annals of botany',
│   │   │   │   'Date': '1923-01',
│   │   │   │   'PageRange': '43--53'
│   │   │   }
│   │   ]
│   }
]

'''
