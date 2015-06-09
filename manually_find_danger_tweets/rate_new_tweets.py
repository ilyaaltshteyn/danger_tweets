# This script just moves manually found tweets into a csv file.

import pandas as pd

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/'
file = 'tweets_from_search_june6th.txt'

tweet_list = []
with open(path + file) as data:
    tweets = data.readlines()
    for tweet in tweets:
        tweet_list.append(tweet)

data = pd.DataFrame(tweet_list)

data['human_coded'] = 0
data['dangerous'] = ''

data.to_csv(path + 'human_rated_tweets_from_search_june6th.csv')