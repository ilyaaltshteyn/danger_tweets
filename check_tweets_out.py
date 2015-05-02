# This script pulls retweets for each tweet 2 hours after it is tweeted, and then again 24 hours after it is tweeted.
filename = '2015-05-02 18:34:15.477448.txt'
path = '/Users/ilya/Projects/danger_tweets/collect tweets/'
file = path + filename

import ast
from os import listdir

with open(path + 'completed_retweet_check_1.txt', 'w') as create_log:
    pass

def file_collector(path):
    with open(path + 'completed_retweet_check_1.txt', 'r') as c:
        completed = c.readlines()
        print completed
        files = [x for x in listdir(path) if x not in completed]

tweets_list = []
with open(file, 'r') as tweets:
    for line in tweets:
        try:
            tweets_list.append(ast.literal_eval(line[:-1]))
        except:
            continue

file_collector(path)
