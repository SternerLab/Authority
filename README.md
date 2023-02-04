# Authority

This is an open-source replication and extension of ["A probabilistic similarity metric for medline records"](https://asistdl.onlinelibrary.wiley.com/doi/pdfdirect/10.1002/asi.20105?casa_token=DNyxGM6qY_EAAAAA:Z59sYoMxRI_28GiMlSwWEiVI25tMiO1XRKwlQR5AUUc-lsJbDF79LPqA9XeAK-8oJbJWgK23f4nTBTZu) and following papers. 

## Installation

Install [Python 3.10](https://www.python.org/downloads/)  
Install [poetry](https://python-poetry.org/) for package management.  

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

Alternatively, mongodb can be setup locally, either natively, or with a container system like docker or singularity:

Install `mongodb` using the [official instructions](https://www.mongodb.com/docs/manual/installation/).  

###### With Docker
MongoDB can be finicky to set up correctly, so an alternative is to install [`docker`](https://www.docker.com/).  
If on MacOS, an alternative is [colima](https://github.com/abiosoft/colima).  
Run `sudo docker run -d -p 27017:27017 -v ~/mongodb_data:/data/db mongo`  
You can get a manual shell with `docker exec -it mongodb bash`  

If running on a supercompute cluster without docker, a viable alternative is to use [singularity](https://asurc.atlassian.net/wiki/spaces/RC/pages/54099969/Building+containers+and+using+Singularity#BuildingcontainersandusingSingularity-WhatisSingularityandwhynotDocker%3F), this guide describes the process for ASU's Agave cluster.


Run `poetry update` to initialize and install all dependencies.  

See instructions in `script\_with\_comments.ipynb` for a reference for the initial version

Create `umls_credentials.json` as follows from info at [umls website](https://documentation.uts.nlm.nih.gov/rest/home.html):
```json
{"email" : "myemail@domain.com",
 "api_key" : "abcdefghi-72139"}
```

Create `bhl_credentials.json` with credentials from [their website](https://www.biodiversitylibrary.org/docs/api3.html).

