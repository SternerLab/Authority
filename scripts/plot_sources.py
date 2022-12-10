import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    # val_df = pd.read_csv('data/authority_validation_metrics.csv')
    val_df = pd.read_csv('data/validation_metrics_lucas.csv')
    # val_df.sort_values(by='article_count', ascending=False, inplace=True)
    print(val_df.columns)
    print(set(val_df['reference_source']))
    print(set(val_df['prediction_source']))
    print(val_df)
    print(val_df.describe())
    columns = ['name', 'article_count', 'accuracy', 'precision', 'recall', 'lumping', 'splitting', 'cluster_precision', 'cluster_recall']
    print(val_df[columns].describe())

    self_scholar = val_df.loc[((val_df['prediction_source'] == 'self_citations') &
                               (val_df['reference_source'] == 'google_scholar'))]
    print(self_scholar.describe())

    sns.catplot(val_df, x='accuracy', y='prediction_source', row='reference_source', kind='violin')
    plt.savefig('plots/source_comparison.png', bbox_inches='tight', dpi=300)
    plt.show()
