import pandas as pd

def load_training(path):
    df = pd.read_csv(path, compression='gzip')
    df = df.sample(frac=1).reset_index(drop=True)
    df.dropna(inplace=True)

    negative = df[df['label'] == False]
    positive = df[df['label'] == True].head(len(negative))
    training = pd.concat([positive, negative])
    return training
