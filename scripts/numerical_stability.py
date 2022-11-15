import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def inference(ratio, prior, eps=1e-10):
    result = 1 / (1 + (1 - prior) / (prior * ratio + eps))
    # print(f'inference: {ratio}, {prior}, {result}')
    return result

def run():
    n, m = 10, 1000
    results = np.zeros((n * m, 3))
    priors = np.linspace(0, 1,     n)
    ratios = np.linspace(30, 0, m)
    for i, prior in enumerate(priors):
        for j, ratio in enumerate(ratios):
            results[i * m + j] = (ratio, prior, inference(ratio, prior))

    df = pd.DataFrame(results, columns=['ratio', 'prior', 'probability'])

    sns.heatmap(df.pivot('prior', 'ratio', 'probability'))
    plt.title('Inference Behavior')
    plt.xlabel('Ratio')
    plt.ylabel('Prior')
    plt.show()
