import pandas as pd

''' Create a giant pandas dataframe containing all of our validation data...
Something like:

    Author    | Title      |
--------------------------------------------------------------------------------
    Tolkien   | On hobbits |

And then a condensed verious for each heuristic and algorithm

Heuristics  ---> Expert Labels

FILN | Authority hueristic | Authority | self-citation | google scholar | BHL
--------------------------------------------------------------------------------
1    |                   1 |         1 |             1 |              1 | 0
1    |                   1 |         1 |             1 |              1 | 1
1    |                   1 |         1 |             0 |              0 | 0
...


'''

# pseudocode:
for pair in all_pairs:
    pair_evals = []
    for eval_method in eval_methods:
        classification = eval_method()
        pair_evals.append(classification)
    pd.add_row(pair_evals)

