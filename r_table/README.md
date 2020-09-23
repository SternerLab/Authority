# Authority model
Python code for the paper [Author name disambiguation in MEDLINE](https://dl.acm.org/doi/pdf/10.1145/1552303.1552304). Inroductory slides are available [here](https://github.com/SternerLab/Authority/blob/initial/r_table/slides/Authority%20look%20up%20table.pptx).

## Software requirements
1. The code requires **Python 3** and please install the Python dependencies with the command:
```bash
pip install -r requirements.txt
```

2. This code requires **MySQL** database setup. Any version above 8.0 should work.

3. This code requires **Matlab R2020a** setup. 

## Execution
1. To compute the entire look up table from xml files (steps a-e), run the command
```bash
cd r_table
.\script.sh
```

a. To parse xml files and store them to the database, run the command
```bash
cd r_table\parser
python main.py --zip_file <zip_file_path_to_be_processed>
```

b. To generate match and non match sets, run the command
```bash
cd r_table\reference_sets
python create_sets.py
```

c. To compute similarities between pairs of the sets, run the command
```bash
cd r_table\compute_r
python compute_similarity.py --update <true, if updating exisiting similarity profiles. false, otherwise>
```

d. To compute r_table from the similarity profiles, run the command
```bash
cd r_table\compute_r
python compute_r.py
```

e. To smoothen r_table, run the command
```bash
```
