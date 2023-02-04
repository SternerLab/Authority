# Authority

This is an open-source replication and extension of ["A probabilistic similarity metric for medline records"](https://asistdl.onlinelibrary.wiley.com/doi/pdfdirect/10.1002/asi.20105?casa_token=DNyxGM6qY_EAAAAA:Z59sYoMxRI_28GiMlSwWEiVI25tMiO1XRKwlQR5AUUc-lsJbDF79LPqA9XeAK-8oJbJWgK23f4nTBTZu) and following papers. 

Broadly, the repository is split into python libraries in the `resolution/` folder and python scripts in the `scripts/` folder. Scripts are invoked using [BASh](https://en.wikipedia.org/wiki/Bash_(Unix_shell)?useskin=vector), such as `./run list`, which will expand to `poetry run python main.py list`, which calls `scripts/list.py`. If BASh isn't available (such as on windows), then the scripts or `main.py` can be run independently.

The `resolution` folder includes six main libraries:  
```
resolution
└───algorithm: Generic tools used by all author resolution algorithms
│
│       inference.py:          Generic InferenceMethod class that supports multiple methods
│                                  including Authority, naive bayes, and xgboost.
│       triplet_violations.py: triplet_corrections used in Authority and ablation studies.
│       components.py:         connected_components used in Authority and ablation studies.
│
└───authority: The replication of the Authority Author Name Disambiguation (AND) algorithm.
│       
│       clustering.py:     Implementation of the agglomerative clustering algorithm described in Torvik 2005/2009/2014
│       compute_ratio.py:  Computes conditional probability ratios described in Torvik 2005/2009/2014
│       features.py:       Defines the manually designed features proposed in Torvik 2005/2009
│       compare.py:        Creates Authority feature vectors
│       inference.py:      Defines the Authority-specific InferenceMethod class
│       interpolate.py:    Computes the feature interpolation described in Torvik 2005
│       smooth.py:         Computes the feature smoothing described in Torvik 2005
│
└───parse: Utilities for parsing JSTOR documents. Could be expanded for other databases/journals
│       
│       files.py:          Helper function for cleanly unpacking a zip file of XML files
│       parse.py:          The various parsing functions, specific to JSTOR articles. 
│
└───baselines: Baselines compared to the Authority method
│       
│       classifier.py:     Base class for a generic classifier baseline (such as naive bayes)
│       cluster.py:        Base class for a generic direct clustering method
│       embedding.py:      Base class for a generic embedding method (such as SciBERT)
│       training_data.py:  Helper functions for turning MongoDB into a CSV of training data
│       utils.py:          Helper functions for training baselines
│
└───validation: Utilities for validating results of baselines and Authority
│       
│       metrics.py:        Various evaluation metrics for validation
│       validate.py:       The primary validation code!
│
│       resolver.py:       Base class defining a ground truth validation method
│       biodiversity.py:   Biodiversity Heritage Library API parsing
│       google_scholar.py: Google scholar API parsing (typically broken, not officially supported)
│       orcid.py:          ORCID database API parsing
│       self_citations.py: Creates ground truth validation data via self citation parsing/resolution
│       scrape.py:         Helper functions for creating ground truth data via scraping
│       heuristic.py:      Common heuristics for comparison, such as last-name-match, or the Authority heuristics
│       semantic_scholar.py: Incomplete, would contain parsing of semantic scholar API
│       manual.py:         Empty, would contain code for manual disambiguation
│       utils.py:          Various validation utilities
│
```


## Installation

Install [Python 3.10](https://www.python.org/downloads/).  
Install [poetry](https://python-poetry.org/) for package management.  

Run `git clone https://github.com/SternerLab/Authority`  
`cd Authority`  
Run `poetry update` to initialize and install all dependencies.  

If you prefer to install packages without poetry (either in virtualenv or globally), you can use:  
`poetry export -f requirements.txt --output requirements.txt` to make a `requirements.txt` file, and use a command like:  
`pip install -r requirements.txt` to install it. However, poetry is recommended.

Next, it will be necessary to setup MongoDB.

#### MongoDB Setup

###### Web-Hosted 

The easiest method for using MongoDB is to use the web-hosted version.
This will require credentials in `mongo_credentials.json`, which can be obtained by emailing the project authors. Simply update the `username` and `password` fields and name the file `mongo_credentials.json`, and do not change the `uri` field unless the database has been migrated elsewhere:  
```json
{"uri" : "mongodb+srv://{credentials}@authorresolution.yprf1.mongodb.net",
 "username" : "my-mongo-user",
 "password" : "abcdefghi-72139"}
```

###### Local Database

**If mongoDB has been setup to connect to web hosting, ignore this section.**

Alternatively, mongodb can be setup locally, either natively, or with a container system like docker or singularity:

Install `mongodb` using the [official instructions](https://www.mongodb.com/docs/manual/installation/).  

###### With Docker
MongoDB can be finicky to set up correctly, so an alternative is to install [`docker`](https://www.docker.com/).  
If on MacOS, an alternative is [colima](https://github.com/abiosoft/colima).  
Run `sudo docker run -d -p 27017:27017 -v ~/mongodb_data:/data/db mongo`  
You can get a manual shell with `docker exec -it mongodb bash`  

If running on a supercompute cluster without docker, a viable alternative is to use [singularity](https://asurc.atlassian.net/wiki/spaces/RC/pages/54099969/Building+containers+and+using+Singularity#BuildingcontainersandusingSingularity-WhatisSingularityandwhynotDocker%3F), this guide describes the process for ASU's Agave cluster.

# Scripts


See instructions in `script\_with\_comments.ipynb` for a reference for the initial version

Create `umls_credentials.json` as follows from info at [umls website](https://documentation.uts.nlm.nih.gov/rest/home.html):
```json
{"email" : "myemail@domain.com",
 "api_key" : "abcdefghi-72139"}
```

Create `bhl_credentials.json` with credentials from [their website](https://www.biodiversitylibrary.org/docs/api3.html).

