# This script pulls retweets for each tweet 2 hours after it is tweeted, and then again 24 hours after it is tweeted.

#Get api details:
api_details = []
with open(path + 'api_details.txt', 'r') as a:
    info = a.readlines()
    api_details.append(info)
api_details = api_details[0][0].split(',')

#Setup api details:
consumer_key = api_details[0]
consumer_secret = api_details[1]
access_token_key = api_details[2]
access_token_secret = api_details[3]


filename = '2015-05-02 18:34:15.477448.txt'
path = '/Users/ilya/Projects/danger_tweets/collect tweets/'
file = path + filename

import ast
from os import listdir

# Create the log
with open(path + 'completed_retweet_check_1_log.txt', 'w') as create_log:
    pass

def logger(path, filename):
    """Adds the name of a given file to the log of checked files."""
    with open(path + 'completed_retweet_check_1_log.txt', 'a') as file:
        file.write(filename + '\n')

def file_collector(path):
    """Checks which files of tweets have not yet been retweet checked.
    Returns list of files that still need to be retweet checked."""
    with open(path + 'completed_retweet_check_1_log.txt', 'r') as c:
        completed = c.readlines()
        print completed
        files = [x for x in listdir(path) if x not in completed]
    return files

def tweets_to_list_converter(path, file):
    """Converts a text file of tweets into a list of dictionaries, each one
    representing a single tweet."""
    tweets_list = []
    with open(file, 'r') as tweets:
        for line in tweets:
            try:
                tweets_list.append(ast.literal_eval(line[:-1]))
            except:
                continue
    return tweets_list

def tweet_to_retweets(tweet):
    """Take a tweet as input and returns its current number of retweets, the
    time at which it was checked, and its tweet ID."""

    print('\nQUOTA: %s' % r.get_rest_quota())

a = file_collector(path)
logger(path, filename)
