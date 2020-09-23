# Authority model
Python code for the paper [Author name disambiguation in MEDLINE](https://dl.acm.org/doi/pdf/10.1145/1552303.1552304). Inroductory slides are available [here]().

## Software requirements
1. The code requires **Python 3** and please install the Python dependencies with the command:
```bash
pip install -r requirements.txt
```

2. This code requires **MySQL** database setup. Any version above 8.0 should work.

3. This code requires **Matlab R2020a** setup. 

## Execution
1. To compute the entire look up table from xml files, run the command
```bash
cd r_table
.\script.sh
```

2. To parse xml files and store them to the database, run the command
```bash
cd r_table\parser
python main.py --zip_file <zip_file_path_to_be_processed>
```

3. To generate match and non match sets, run the command
```bash
cd r_table\reference_sets
python create_sets.py
```

4. To compute similarities between pairs of the sets, run the command
```bash
cd r_table\compute_r
python compute_similarity.py --update <true, if updating exisiting similarity profiles. false, otherwise>
```

5. To compute r_table from the similarity profiles, run the command
```bash
cd r_table\compute_r
python compute_r.py
```

6. To smoothen r_table, run the command
```bash
```
