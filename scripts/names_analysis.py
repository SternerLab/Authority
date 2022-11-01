import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    names_df = pd.read_csv('names.csv')
    names_df.sort_values(by='count', ascending=False, inplace=True)
    print(names_df.head(10)[['name', 'count']])
    # sns.displot(names_df, x='count', log_scale=True)
    # plt.savefig('plots/name_frequencies.png')
    # plt.show()
    # plt.clf()
