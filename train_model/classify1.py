import pandas as pd

dat = pd.read_csv('/Users/ilya/Projects/danger_tweets/train_model/study2_minimal_outof_psql.csv', header = -1, columns = ['tweet', 'danger', 'non_danger'])

