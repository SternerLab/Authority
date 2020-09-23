# About
This module contains 
1. code to compute similarity vector x = <x1, x2, x3, x4, x5, x7> between all pairs of articles in article_match_set, article_non_match_set, name_match_set and name_non_match_set.

2. code to compute r(x).

# Computing x
x is calculated by individually computing its attributes. More details in the [paper](https://asistdl.onlinelibrary.wiley.com/doi/pdf/10.1002/asi.20105?casa_token=aH8v2-ZPwNMAAAAA:wZY6XqC6U2H5ldwK7YyzmsX0pkJ7qVmRoQhDon4Is3eakaL4i-KB58a_GWFDnDNI56PAl53MP1Ig8g). 

```
x1 = 3 if init2A = init2B and both are given (e.g., (A, A)), 2 if init2A = init2B and both are not given (i.e., (∅︁, ∅︁)), 1 if init2A ≠ init2B and one is not given (e.g., (A, ∅︁)), and 0 if init2A ≠ init2B and both are given (e.g., (A, B)).

x2 = 1 if suffA = suffB and both are given (e.g., (Jr, Jr)), and 0 otherwise,

x3 = | titleA ∩ titleB|,

x4 = 1 if jrnlA = jrnlB, and 0 otherwise,

x5 = |coauthA ∩ coauthB|,

x7 = 3 if langA = langB and non‐English (e.g., (jpn, jpn)), 2 if langA = langB and English (i.e., (eng, eng)), 1 if langA ≠ langB and one is English (e.g., (eng, jpn)), and

0 if langA ≠ langB and both are non‐English (e.g., (jpn, fre)).
```

x1 , x2 are computed on pairs belonging to name_sets.
x3, x4, x5, x7 are considered as xa and are computed on pairs belonging to article_sets.

## Usage
To compute similarity profiles, run the command
```bash
python .\compute_x.py --update true
```

## output files
The above command generates the following json files:
```
1. x1_m.json
2. x1_nm.json
3. x2_m.json
4. x2_nm.json
5. xa_m.json
6. xa_nm.json
```

These json files are dictionaries which stores the values of x as keys and their frequencies as values. x1_m.json is a dictionary containing x1 values as keys and their frequencies as values when pairs belonging to matching set are considered. 

Example: if x1_m.json contains 
```bash
{"3": 10, "1": 2, "0": 4}
```
it implies that in the matching set, there are 10 pairs with x1 = 3; 2 pairs with x1 = 1; 4 pairs with x1 = 0.


