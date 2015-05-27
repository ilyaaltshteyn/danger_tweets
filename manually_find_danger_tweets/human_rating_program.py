# This script presents each tweet to a human rater for rating. It then puts a
# 1 in the 'human_coded' column in that tweet's row in the csv file called
# 'human_rated_tweets_from_search.csv', and puts the human rating into the 
# "dangerou" column in that csv file.

import pandas as pd

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/'

data = pd.read_csv(path + 'human_rated_tweets_from_search.csv')

for row in range(len(data)):
    if data.ix[row,'human_coded'] == 0:
        data.ix[row,'human_coded'] = 1
        data.ix[row,'dangerous'] = raw_input(data.ix[row,1])
        data.to_csv(path + 'human_rated_tweets_from_search.csv', index = False)

