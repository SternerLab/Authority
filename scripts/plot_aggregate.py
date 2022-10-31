import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    # val_df = pd.read_csv('authority_validation_metrics_october31_backup.csv')
    val_df = pd.read_csv('authority_validation_metrics_backup.csv')
    val_df.fillna(0, inplace=True)
    print(val_df)
    print(val_df.describe())

    metrics = ('lumping', 'splitting', 'accuracy')
    for metric in metrics:
        fig = sns.displot(val_df, x=metric)
        fig.set_axis_labels(metric.title(), 'Frequency')
        fig.savefig(f'plots/{metric}_frequency.png')
        plt.show()
        plt.clf()

    names_df = pd.read_csv('names.csv')
    print(names_df)
    sns.displot(names_df, x='count', log_scale=True)
    plt.savefig('plots/name_frequencies.png')
    plt.show()
    plt.clf()

    lookup = dict()
    for tup in track(names_df.itertuples(), total=names_df.shape[0]):
        lookup[tup.name] = tup.count

    frequencies = np.zeros(val_df.shape[0])
    for i, tup in track(enumerate(val_df.itertuples()), total=val_df.shape[0]):
        frequencies[i] = lookup.get(tup.name, 0)
    val_df['frequency'] = frequencies
    val_df.to_csv('composite.csv')

    plt.clf()
    composite = pd.read_csv('composite.csv')
    print(composite['frequency'].describe())
    print(composite['frequency'].max())
    for metric in metrics:
        ax = sns.scatterplot(composite, x='frequency', y=metric)
        ax.set_xlabel('Name Frequency')
        ax.set_ylabel(metric.title())
        plt.savefig(f'plots/{metric}_name_frequency.png')
        plt.show()
        plt.clf()

