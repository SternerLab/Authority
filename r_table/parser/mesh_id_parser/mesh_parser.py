import requests
# import sys
# sys.path.append('../../')
# from SQL.SQLClient import SQLClient
import json
import re

# # sql_client = SQLClient()
# # sql_client.connect_to_db("test1")

# # query = 'select distinct id, title from articles where journal_name like \'%taxon%\''
# # results = sql_client.execute_and_fetch(query)

# api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=1000&term={}&field=title'
# result_dict = {}
# for result in results:
#     title = result[1]
#     title = title.replace(' ', '%20')
#     api_with_title = api.format(title)
#     print(api_with_title)
#     response = requests.get(api_with_title).json()
#     # if response.status_code == 200:
#     search_result = response["esearchresult"]
#     if search_result is not None and int(search_result["count"]) > 0:
#         pmid = search_result["idlist"][0]
#         result_dict[result[0]] = pmid
# print(result_dict)


# with open('mesh_taxon.json', 'w+') as f:
#     json.dump(result_dict, f)

def get_mesh_and affiliation_terms(title):
    api = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=1000&term={}&field=title'
    mesh_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}"

    title = title.replace(' ', '%20')
    api_with_title = api.format(title)
    response = requests.get(api_with_title).json()
    search_result = response["esearchresult"]
    if search_result is not None and int(search_result["count"]) > 0:
        pmid = search_result["idlist"][0]
        mesh_api_with_pmid = mesh_api.format(pmid)
        response = requests.get(mesh_api_with_pmid).text
        mesh_pattern = re.compile('.*term \"([A-Z a-z]*)\".*', re.MULTILINE)
        mesh_terms = re.findall(mesh_pattern, response.text)
        affiliation_pattern = re.compile('.*name ml \"([A-Z a-z.]*)\",\n.*affil str.\"([^\"]*)\"\n[ ]*}')
        affiliation_terms = re.findall(affiliation_pattern, response.text)
        return mesh_terms, affiliation_terms


# # api = api.format('Adaptation Reviewed: A Phylogenetic Methodology for Studying Character Macroevolution')


# api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30456532"
api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=15805007"
response = requests.get(api)

pattern = re.compile('.*term \"([A-Z a-z]*)\".*', re.MULTILINE)
affiliation_pattern = re.compile('.*name ml \"([A-Z a-z.]*)\",\n.*affil str.\"([^\"]*)\"\n[ ]*}')

terms = re.findall(affiliation_pattern, response.text)
print(terms)
