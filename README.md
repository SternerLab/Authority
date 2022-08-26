# Authority

## Installation

Install `mongodb` using the [official instructions](https://www.mongodb.com/docs/manual/installation/).  
MongoDB can be finicky to set up correctly, so an alternative is to install [`docker`](https://www.docker.com/) and then run `sudo docker run -d -p 27017:27017 -v ~/mongodb_data:/data/db mongo`. You can get a manual shell with `docker exec -it mongodb bash`  
Install [Python 3.10](https://www.python.org/downloads/)  
Install [poetry](https://python-poetry.org/) for package management.  

Run `poetry update` to initialize and install all dependencies.  

See instructions in `script\_with\_comments.ipynb` for a reference for the initial version

Create `umls_credentials.json` as follows from info at [umls website](https://documentation.uts.nlm.nih.gov/rest/home.html):
```json
{"email" : "myemail@domain.com",
 "api_key" : "abcdefghi-72139"}
```

