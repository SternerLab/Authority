import seaborn as sns
import matplotlib.pyplot as plt

def probability_matrix(cluster, show=True):
    for prior_key in ('match_prior', 'prior'):
        prior = cluster['prior']
        print(f'{prior_key} : {prior:.4%}')
    for prob_key in ('probs', 'original_probs', 'fixed_probs'):
        probs = pickle.loads(cluster[prob_key])
        plt.cla(); plt.clf(); plt.close(); # To avoid multiple cbars
        axes = sns.heatmap(probs, vmin=0., vmax=1.)
        axes.set_xlabel('Paper')
        axes.set_ylabel('Paper')
        axes.set_title(f'Pairwise probabilities for papers authored by {name}')
        fig  = axes.get_figure()

        fig.savefig(f'plots/probability_matrices/{name}_{prob_key}.png')
        if show and len(cluster['cluster_labels']) > 4:
            plt.show()
