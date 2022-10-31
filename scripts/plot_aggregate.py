import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from rich.progress import track

def run():
    val_df = pd.read_csv('authority_validation_metrics_october31_backup.csv')
    val_df.fillna(0, inplace=True)
    print(val_df)
    print(val_df.describe())

    for metric in ('lumping', 'splitting', 'accuracy'):
        fig = sns.displot(val_df, x=metric)
        fig.set_axis_labels(metric.title(), 'Frequency')
        fig.savefig(f'plots/{metric}_frequency.png')
        plt.show()
        plt.clf()

    val_df['frequency'] = 0
    names_df = pd.read_csv('names.csv')
    print(names_df)
    sns.displot(names_df, x='count', log_scale=True)
    plt.savefig('plots/name_frequencies.png')
    plt.show()
    plt.clf()

    for tup in track(names_df.itertuples(), total=names_df.shape[0]):
        queried = val_df[val_df.name == tup.name]
        if queried.empty:
            continue
        queried['frequency'] = tup.count
    val_df.to_csv('composite.csv')

    plt.clf()
    composite = pd.read_csv('composite.csv')
    print(composite)
    sns.scatterplot(composite, x='frequency', y='accuracy')
    plt.show()
    plt.clf()

