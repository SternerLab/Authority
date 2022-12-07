import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    val_df = pd.read_csv('data/authority_validation_metrics.csv')
    val_df.fillna(0, inplace=True)
    print(val_df.describe())

    names_df = pd.read_csv('data/names.csv')

    lookup = dict()
    for tup in track(names_df.itertuples(), total=names_df.shape[0]):
        lookup[tup.name] = tup.count

    frequencies = np.zeros(val_df.shape[0])
    for i, tup in track(enumerate(val_df.itertuples()), total=val_df.shape[0]):
        frequencies[i] = lookup.get(tup.name, 0)
    val_df['frequency'] = frequencies
    val_df = val_df[val_df['article_count'] > 1]
    val_df.sort_values(by='article_count', ascending=False, inplace=True)
    val_df.to_csv('data/composite.csv')

    prediction_df = val_df[val_df['prediction_source'] == 'predicted']
    prediction_df.describe().to_csv('data/aggregate.csv')
    print(prediction_df.describe())

    columns = ['name', 'article_count', 'accuracy', 'precision', 'recall', 'lumping', 'splitting', 'cluster_precision', 'cluster_recall']
    print('all')
    print(prediction_df[columns].describe())
    print('top/bottom')
    print(prediction_df.head(30)[columns])
    print(prediction_df.tail(30)[columns])
    print('top 100')
    print(prediction_df.head(100)[columns].describe())
    print('bottom 100')
    print(prediction_df.tail(100)[columns].describe())
    prediction_df.sort_values(by='accuracy', ascending=True, inplace=True)
    print(prediction_df.head(10))
    print(prediction_df.tail(10))

    metrics = ('lumping', 'splitting', 'accuracy')
    print(val_df['frequency'].describe())
    print(val_df['frequency'].max())
    for metric in metrics:
        fig = sns.relplot(val_df, x='frequency', y=metric, col='prediction_source')
        fig.set(xlabel='Name Frequency', ylabel=metric.title())
        # ax = sns.scatterplot(val_df, x='frequency', y=metric, hue='prediction_source')
        plt.savefig(f'plots/{metric}_name_frequency.png', bbox_inches='tight', dpi=300)
        plt.show()
        plt.clf()

