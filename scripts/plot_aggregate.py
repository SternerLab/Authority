import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    # val_df = pd.read_csv('data/authority_validation_metrics.csv')
    # val_df = pd.read_csv('scholar_metrics_nov_14_manuha.csv')
    val_df = pd.read_csv('scholar_metrics_nov_14_lucas.csv')
    val_df.fillna(0, inplace=True)
    print(val_df)
    print(val_df.describe())

    metrics = ('lumping', 'splitting', 'accuracy')
    for metric in metrics:
        plt.clf()
        fig = sns.displot(val_df, x=metric)
        fig.set_axis_labels(metric.title(), 'Frequency')
        plt.show()
        fig.savefig(f'plots/{metric}_frequency.png')
        plt.clf()

    names_df = pd.read_csv('data/names.csv')
    print(names_df)
    plt.clf()
    sns.displot(names_df, x='count', log_scale=True)
    plt.show()
    plt.savefig('plots/name_frequencies.png')
    plt.clf()

    lookup = dict()
    for tup in track(names_df.itertuples(), total=names_df.shape[0]):
        lookup[tup.name] = tup.count

    frequencies = np.zeros(val_df.shape[0])
    for i, tup in track(enumerate(val_df.itertuples()), total=val_df.shape[0]):
        frequencies[i] = lookup.get(tup.name, 0)
    val_df['frequency'] = frequencies
    val_df = val_df[val_df['article_count'] > 1]
    val_df.sort_values(by='article_count', ascending=False, inplace=True)
    print(val_df.describe())
    columns = ['name', 'article_count', 'accuracy', 'precision', 'recall', 'lumping', 'splitting', 'cluster_precision', 'cluster_recall']
    print('all')
    print(val_df[columns].describe())
    print('top/bottom')
    print(val_df.head(30)[columns])
    print(val_df.tail(30)[columns])
    print('top 100')
    print(val_df.head(100)[columns].describe())
    print('bottom 100')
    print(val_df.tail(100)[columns].describe())
    val_df.sort_values(by='accuracy', ascending=True, inplace=True)
    print(val_df.head(10))
    print(val_df.tail(10))
    val_df.describe().to_csv('data/aggregate.csv')
    val_df.to_csv('data/composite.csv')

    plt.clf()
    composite = pd.read_csv('data/composite.csv')
    print(composite['frequency'].describe())
    print(composite['frequency'].max())
    for metric in metrics:
        ax = sns.scatterplot(composite, x='frequency', y=metric)
        ax.set_xlabel('Name Frequency')
        ax.set_ylabel(metric.title())
        plt.savefig(f'plots/{metric}_name_frequency.png')
        plt.clf()

