from authority.parse.citation_crossref import crossref_citation
from rich.pretty import pprint

ref = 'Tarafdar J C and Ciaassen N 1988 Organic phosphorus compounds as a phosphorus source for higher plant through the activity of phosphatase produced by plant roots and microorganisms. Biol.'

def run():
    pprint(crossref_citation(ref))
