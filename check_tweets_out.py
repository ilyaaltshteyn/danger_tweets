# This script pulls retweets for each tweet 2 hours after it is tweeted, and then again 24 hours after it is tweeted.

# ----****** FIRST, CREATE THE API CALLER *****------

import oauth2
import time
import urllib2
import json

path = '/Users/ilya/Projects/danger_tweets/collect tweets/'

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

#Create api searcher:
url1 = 'https://api.twitter.com/1.1/statuses/lookup.json'
params = {
    "oauth_version": "1.0",
    "oauth_nonce": oauth2.generate_nonce(),
    "oauth_timestamp": int(time.time())
}
consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth2.Token(key=access_token_key, secret=access_token_secret)
params["oauth_consumer_key"] = consumer.key
params["oauth_token"] = token.key

def api_request(list_of_tweets):
    """Takes a list of up to 100 tweet ids and returns tweet details, including
    retweet count. Tweets in original list must be strings."""
    tweets_as_strings = ','.join(list_of_tweets)
    url = url1
    params['id'] = tweets_as_strings
    params['map'] = 'true'
    req = oauth2.Request(method="GET", url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)
    headers = req.to_header()
    url = req.to_url()
    response = urllib2.Request(url)
    tweets = urllib2.urlopen(response)
    return json.load(tweets)



# ----****** DEFINE FUNCTIONS THAT WILL PRODUCE LISTS OF TWEETS *****----

import ast
from os import listdir


def file_collector(path):
    """Checks which files of tweets have not yet been hydrated.
    Returns list of files that still need to be hydrated."""
    with open(path + 'hydrated_tweets_log.txt', 'r') as c:
        hydrated = c.readlines()
        files = [x for x in listdir(path) if x not in hydrated]
    return files

def logger(path, filename):
    """Adds the name of a given file to the log of hydrated tweets files."""
    with open(path + 'hydrated_tweets_log.txt', 'a') as file:
        file.write(filename + '\n')

def tweets_to_list_converter(file):
    """Converts a text file of tweets into a list of tweet ids, each one
    representing a single tweet. Adds the name of the text file to the log that
    keeps track of files that have been hydrated."""
    tweets_list = []
    with open(file, 'r') as tweets:
        for line in tweets:
            try:
                one_tweet_id = ast.literal_eval(line[:-1])['id']
                tweets_list.append(one_tweet_id)
            except:
                continue
    return tweets_list

filename = '2015-05-02 18:34:15.477448.txt'
path = '/Users/ilya/Projects/danger_tweets/collect tweets/'
stuff = tweets_to_list_converter(path + filename)

def tweet_to_retweets(tweet):
    """Take a tweet as input and returns its current number of retweets, the
    time at which it was checked, and its tweet ID."""

    print('\nQUOTA: %s' % r.get_rest_quota())

r = api.request('statuses/sample', {'country':'United States',
            'language' : 'en'})

a = file_collector(path)
logger(path, filename)

# ----**** NOW ACTUALLY RUN ALL THOSE FUNCTIONS TO GET HYDRATED DATA! ***---

# Create the log:
with open(path + 'hydrated_tweets_log.txt', 'w') as create_log:
    pass

filename = '2015-05-02 18:34:15.477448.txt'
path = '/Users/ilya/Projects/danger_tweets/collect tweets/'
file = path + filename
