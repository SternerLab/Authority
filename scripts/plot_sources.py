import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np

from rich.progress import track

def run():
    val_df = pd.read_csv('data/resolution_validation_metrics.csv')
    print(val_df.columns)
    print(set(val_df['reference_source']))
    print(set(val_df['prediction_source']))
    print(val_df)
    print(val_df.describe())
    val_df.fillna(0., inplace=True)
    all_metrics = ['accuracy', 'precision', 'recall', 'neg_precision', 'neg_recall', 'f1', 'lumping', 'splitting', 'cluster_precision', 'cluster_recall', 'adjusted_rand', 'adjusted_mutual_info', 'homogeneity', 'completeness', 'v_measure', 'fowlkes_mallows']
    metrics = all_metrics
    # metrics = ['adjusted_mutual_info']
    columns = ['name', 'article_count'] + metrics
    print(val_df[columns].describe())

    self_scholar = val_df.loc[((val_df['prediction_source'] == 'self_citations') &
                               (val_df['reference_source'] == 'google_scholar'))]
    print(self_scholar[columns].describe())

    sns.catplot(val_df, x='accuracy', y='prediction_source', row='reference_source', kind='violin')
    plt.savefig('plots/source_comparison_violins.png', bbox_inches='tight', dpi=300)
    plt.show()

    # true_sources = {'google_scholar'}#, 'self_citations', 'biodiversity'}
    true_sources = {'biodiversity', 'google_scholar'}
    # true_sources = {'self_citations'}
    # eval_sources = {'authority', 'xgboost_components', 'naive_bayes_components', 'merge_heuristic', 'split_heuristic'}
    eval_sources = {'authority', 'authority_legacy',
                    'self_citations',
                    'xgboost', 'naive_bayes',
                    'merge_heuristic', 'split_heuristic',
                    'meshcoauthor_heuristic', 'name_heuristic'}

    true_val_df = val_df.loc[((val_df['prediction_source'].isin(eval_sources)) &
                              (val_df['reference_source'].isin(true_sources)))]
    print(true_val_df[columns].describe())

    metrics_df = pd.melt(true_val_df, id_vars=['prediction_source'],
                         value_vars=columns[2:],
                         var_name='metric', value_name='metric_value')
    # metrics_df.dropna(inplace=True)
    print(metrics_df)
    fig = sns.catplot(metrics_df, y='metric', x='metric_value', row='prediction_source', kind='bar')
    for ax in fig.axes.ravel():
        for c in ax.containers:
            labels = [f'  {v.get_width():.2%}' for v in c]
            ax.bar_label(c, labels=labels, label_type='edge')
    plt.savefig('plots/multi_source_validation.png', bbox_inches='tight', dpi=300)
    plt.show()

