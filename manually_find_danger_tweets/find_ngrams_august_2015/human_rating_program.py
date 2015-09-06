#!/usr/local/bin/python

# This script presents each tweet to a human rater for rating. It then puts a
# 1 in the 'human_coded' column in that tweet's row in the csv file called
# 'human_rated_tweets_from_search.csv', and puts the human rating into the 
# "dangerou" column in that csv file.

import pandas as pd
# import numpy as np

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/find_ngrams_august_2015/'
# filename = 'target_danger_ngram_tweets.txt'
# file_length = sum(1 for line in open(path + filename))

# data = pd.DataFrame(columns = ['tweet', 'human_coded', 'dangerous'])
# data['tweet'] = np.zeros(file_length)
# data['human_coded'] = np.zeros(file_length)
# data['dangerous'] = np.zeros(file_length)


# with open(path + filename, 'r') as infile:
#     for tweet in range(file_length):
#         data.ix[tweet, 'tweet'] = infile.readline()

# data.to_csv(path + 'ngram_tweets_hand_coded.csv')

data = pd.read_csv(path + 'ngram_tweets_hand_coded_2.csv')



for row in range(len(data)):
    if data.ix[row,'human_coded'] == 0:
        data.ix[row,'human_coded'] = 1
        data.ix[row,'dangerous'] = raw_input(data.ix[row,'tweet'])
        data.to_csv(path + 'ngram_tweets_hand_coded_2.csv', index = False)

