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

    true_sources = {'biodiversity', 'google_scholar', 'orcid'}

    pairings = {'meta_validation' : ({'self_citations'} | true_sources),
                'ablation_study'  : {'authority_legacy', 'authority_clipped',
                                     'authority_no_correction', 'authority_mixed',
                                     'authority', 'authority_mixed_no_correction',
                                     'authority_no_correction_robust'},
                'heuristic_validation':  {'merge_heuristic', 'split_heuristic',
                        'mesh_coauthor_heuristic', 'name_heuristic'
                        'first_name_heuristic'},
                'baselines' : {'xgboost', 'naive_bayes', 'scidebert_clustering', 'scibert_clustering'}

                }
    for name, eval_sources in pairings.items():
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
        plt.savefig(f'plots/{name}_multi_source_validation.png', bbox_inches='tight', dpi=300)
        plt.show()

