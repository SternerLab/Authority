import pandas as pd

''' Create a giant pandas dataframe containing all of our validation data...
Something like:

    Author    | Title      |
--------------------------------------------------------------------------------
    Tolkien   | On hobbits |

And then a condensed version for each heuristic and algorithm

Heuristics  ---> Expert Labels

      set FILN | Authority hueristic | Authority | self-citation | google scholar | BHL
          -----------------------------------------------------------------------------
pair      1    |                   1 |         1 |             1 |              1 | 0
          1    |                   1 |         1 |             1 |              1 | 1
          1    |                   1 |         1 |             0 |              0 | 0
...


Upper bound:
all distinct

Lower bound:
first name last name all distinct

'''

# # pseudocode:
# for pair in all_pairs:
#     pair_evals = []
#     for eval_method in eval_methods:
#         classification = eval_method()
#         pair_evals.append(classification)
#     pd.add_row(pair_evals)

