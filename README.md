# Authority Replication and Evaluation

This is an open-source replication and extension of ["A probabilistic similarity metric for medline records"](https://asistdl.onlinelibrary.wiley.com/doi/pdfdirect/10.1002/asi.20105?casa_token=DNyxGM6qY_EAAAAA:Z59sYoMxRI_28GiMlSwWEiVI25tMiO1XRKwlQR5AUUc-lsJbDF79LPqA9XeAK-8oJbJWgK23f4nTBTZu) and following papers. 

Broadly, the repository is split into python libraries in the `resolution/` folder and python scripts in the `scripts/` folder. The following sections provide an overview of the libraries and scripts in this repository. See [Installation](#Installation) for install instructions.

# Libraries

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

# Scripts

Scripts are invoked using [BASh](https://en.wikipedia.org/wiki/Bash_(Unix_shell)?useskin=vector), such as `./run list`, which will expand to `poetry run python main.py list`, which calls `scripts/list.py`. If BASh isn't available (such as on windows), then the scripts or `main.py` can be run independently. Note that windows users can install [git
bash](https://git-scm.com/downloads).

#### With an Existing Database
If starting from an existing database, the most important scripts are:
```
./run inference            # Runs the Authority algorithm and ablations
./run validate             # Runs validation with all sources
./run plot_sources         # Creates the main plots used in the paper
```

It may also be desirable to re-train baselines, even though their parameters are already stored in MongoDB. The SciBERT baseline is currently not trained, only evaluated:  
```
./run naive_bayes_baseline # Train the Naive Bayes baseline
./run xgboost_baseline     # Train the XGBoost baseline
./run baselines            # Run inference with all baselines
```

To experiment with the ratio table:
```
./run ratio_table          # Re-calculates the ratio table and saves it to the database
```

#### Replicating from Scratch
If starting from scratch, the `./run parse` script will populate the JSTOR articles database. There is also a `./run all` script that will reproduce results from scratch

```
./run all # Run parsing, subsetting, sampling, the authority algorithm, ablations, baselines, and validation.
# It will individually run:
./run parse        # Parse JSTOR articles from XML (filtering for validity)
./run mesh_from_text # Load MeSH from text
./run subset       # Subset JSTOR articles into Authority blocks
./run sample_pairs # Sample pairs of articles to create initial training data
./run features     # Calculate and cache the feature vectors of article pairs
./run ratio_table  # Calculate and save the ratio table
./run inference    # Run the Authority inference method and its ablations
./run baselines    # Run all baselines
./run validate     # Run validation with all sources
```

MeSH terms will need to be parsed from either the (very slow) NIH API, or from a cached text file:
```
./run mesh # Exceptionally slow (days, if ever)!!
./run mesh_from_text # Expects a mesh_pre_fetched_txt/ directory
```

To use the NIH API from Python, create `umls_credentials.json` as follows from info at [umls website](https://documentation.uts.nlm.nih.gov/rest/home.html):
```json
{"email" : "myemail@domain.com",
 "api_key" : "abcdefghi-72139"}
```

#### Validation Sources
Validation sources are modular, and can be created independently. If using an existing database, they will be pre-populated.
```
./run download_bhl_most_frequent # Recommended script for creating BHL database
./run match_bhl                  # Run after downloading BHL to match to Authority, 
                                 # requires that ./run parse has already run
./run orcid          # Create the ORCID validation data
./run self_citations # Create self citation validation data
./run scholar        # (Try to) create the Google Scholar validation data (usually fails)
```

Each validation source typically requires its own credentials:


Create `bhl_credentials.json` with credentials from [their website](https://www.biodiversitylibrary.org/docs/api3.html).
```json
{"api_key" : "lettersandnumbers123"}
```

Create `orcid_credentials.json` with credentials from [their website](https://info.orcid.org/documentation/api-tutorials/).
```json
{"id" : "APP-MYID", "api_key" : "lettersandnumbers123"}
```



###### Other Scripts

There about 70 different scripts in total, many perform one-off utilities such as creating plots, finding ambiguous authors or finding overlap in validation sources.
All scripts with the `verify_` prefix print debug info or perform sanity checks to ensure that the algorithm has been executed correctly.


# Installation

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
{"uri" : "authorresolution.yprf1.mongodb.net",
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
