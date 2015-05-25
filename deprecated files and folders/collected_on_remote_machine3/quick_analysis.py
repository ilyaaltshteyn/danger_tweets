import os
import ast
import pandas as pd

dir = "/Users/ilya/Projects/danger_tweets/collected_on_remote_machine3/unhydrated_tweets"

files = os.listdir(dir + '/')

def tweet_separator(file):
    """Pulls tweets in and separate them into separate elements, and puts them
    in a list. Returns the list. Only works for hydrated tweets files, bc
    the tweets there are all in one line."""
    tweets_list = []
    with open(file, 'r') as f:
        x = ast.literal_eval(f.readlines()[0][8:-2])
        for item in x.items():
            tweets_list.append(item)
    return tweets_list


# Not using tweet separator function below because I'm looking @ unhydrated tweets:
lengths = []
problems = []
for file in files:
    # try:
        with open(dir + '/' + file,'r') as f:
            x = f.readlines()
            lengths.append(len(x))


print '%d files with %d total tweets' % (len(lengths), np.sum(lengths))
# The total number of tweets we have right now is 10358. That's from 88 files,
# which is a collection spanning 22 hours. At that rate, we get over 11k
# per day.


