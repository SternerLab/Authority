import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import logging
log = logging.getLogger('rich')

from datetime import datetime

from rich.progress import track
true_sources = {'biodiversity', 'google_scholar', 'orcid'}
all_pairings = {'meta_validation' : ({'self_citations'} | true_sources),
                'ablation_study'  : {'authority_legacy', 'authority_clipped',
                                     'authority_no_correction',
                                     'authority_mixed',
                                     'authority',
                                      'authority_mixed_no_correction',
                                     'authority_no_correction_robust',
                                     # 'authority_legacy_ratios',
                                     'authority_torvik_ratios'},
                'heuristic_validation':  {'merge_heuristic', 'split_heuristic',
                        'mesh_coauthor_heuristic', 'name_heuristic', 'full_name_heuristic'},
                # 'baselines' : {'xgboost', 'naive_bayes', 'scibert_clustering'}
                'custom' : {'xgboost', 'naive_bayes', 'authority', 'authority_legacy',
                            'authority_torvik_ratios', 'authority_no_correction',
                            'authority_clipped',
                            'authority_robust_no_correction_robust', # 'authority_mixed',
                            'self_citations'}
                }

all_metrics = ['adjusted_balanced_accuracy', 'accuracy', 'precision', 'recall', 'f1', 'neg_precision', 'neg_recall', 'neg_f1', 'lumping', 'alt_lumping', 'splitting',
               # 'cluster_precision', 'cluster_recall',
               'adjusted_rand', 'adjusted_mutual_info', 'homogeneity', 'completeness', 'v_measure', 'fowlkes_mallows',
'tn_ratio', 'pos_ratio', 'neg_ratio']

analysis_matrix = [# ('mutual_info', ['adjusted_mutual_info'], all_pairings),
                   # ('all', all_metrics, all_pairings),
                   ('baselines', all_metrics, dict(custom=all_pairings['custom'])),
                   ('heuristics', all_metrics, dict(heuristics=all_pairings['heuristic_validation']))
                   # ('merge_ratio', ['merge_ratio'], all_pairings),
                   #('imbalance', ['pos_ratio', 'neg_ratio'], {k : v for k, v in all_pairings.items() if k in {'heuristic_validation', 'meta_validation'}} | {'authority' : {'authority'}})
                   ]

def run():
    val_df = pd.read_csv('data/resolution_validation_metrics.csv')
    print(val_df.columns)
    print(set(val_df['reference_source']))
    print(set(val_df['prediction_source']))
    print(val_df)
    print(val_df.describe())
    # val_df.fillna(0., inplace=True)
    metrics = all_metrics
    time = datetime.now()
    time_str = time.strftime('%b_%d_%Y').lower()
    sub_df = val_df # If we want to subset, do it here
    for metrics_type, metrics, pairings in analysis_matrix:
        columns = ['name'] + metrics
        print(sub_df[columns].describe())
        print(f'Reference cluster stats')
        print(sub_df['n_ref_clusters'].min())
        print(sub_df['n_ref_clusters'].max())
        print(sub_df['n_ref_clusters'].mean())

        for name, eval_sources in pairings.items():
            print(name, eval_sources)
            try:
                true_val_df = sub_df.loc[((sub_df['prediction_source'].isin(eval_sources)) &
                                          (sub_df['reference_source'].isin(true_sources)))]
                print(true_val_df[columns].describe())

                metrics_df = pd.melt(true_val_df, id_vars=['prediction_source'],
                                     value_vars=columns[2:],
                                     var_name='metric', value_name='metric_value')
                # metrics_df.dropna(inplace=True)
                print(f'Metrics DF:')
                print(metrics_df)
                fig = sns.catplot(metrics_df, y='metric', x='metric_value', row='prediction_source', kind='bar')
                for ax in fig.axes.ravel():
                    for c in ax.containers:
                        labels = [f'  {v.get_width():.2%}' for v in c]
                        ax.bar_label(c, labels=labels, label_type='edge')
                plt.savefig(f'plots/{time_str}_{name}_multi_source_validation_{metrics_type}.png',
                            bbox_inches='tight', dpi=300)
                plt.show()
            except ValueError:
                log.warning(f'Could not plot {eval_sources}, no data')

