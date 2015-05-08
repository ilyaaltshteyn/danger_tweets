# This script pulls retweets for each tweet 2 hours after it is tweeted, and then again 24 hours after it is tweeted.

import oauth2, time, urllib2, json, logging, signal
from config import *
from TwitterAPI import TwitterAPI
import time
from datetime import datetime, timedelta
import numpy as np
import signal
import ast
from os import listdir

# Setup file logging and make sure you're in the script's own directory:
import logging, os
# current_dir = os.path.dirname(os.path.realpath(__file__))
current_dir = '/Users/ilya/Projects/danger_tweets/collect tweets'
os.chdir(current_dir)
logging.basicConfig(filename='debug_01_hydrate_2_hrs.log', level=logging.DEBUG)  
path = str(current_dir)

# Define cycle_length, which is the seconds that a single raw tweets file spans
cycle_length = 3600

# Make it so the script dies after a certain amount of time, and sleeps before
# starting so it's properly synced with pull_from_streaming_api.py
signal.alarm(79300)
time.sleep(cycle_length*2)

# Create the log for both hydration times:
with open(path + '/hydrated_tweets_log_2_hrs.txt', 'w') as create_log:
    pass
with open(path + '/hydrated_tweets_log_72_hrs.txt', 'w') as create_log:
    pass
### ---- SETUP API REQUEST FUNCTION

#Get api details:
api_details = []
with open(path + '/api_details.txt', 'r') as a:
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

# ****-----------NOW get list of tweets files and hydrate tweets:

path = str(current_dir) + '/collected_original_tweets'

def tweets_to_list_converter(file):
    """Converts a text file of tweets into a list of tweet ids, each one
    representing a single tweet."""
    tweets_list = []
    with open(file, 'r') as tweets:
        for line in tweets:
            try:
                one_tweet_id = ast.literal_eval(line[:-1])['id']
                tweets_list.append(str(one_tweet_id))
            except:
                logging.exception(Exception)
                continue
    return tweets_list




for x in range(100):
    delay = 2 #seconds
    
    cutoff_time = datetime.now() + timedelta(seconds = cycle_length)

    # Get list of tweet files to hydrate:
    files_list = sorted(listdir(path))
    print files_list
    # Remove some files from the list that are not data files:

    files_list.remove('01_hydrated_tweets_2_hrs')
    files_list.remove('02_hydrated_tweets_72_hrs')
    if 'hydrated_tweets_log_2_hrs.txt' in files_list:
        files_list.remove('hydrated_tweets_log_2_hrs.txt')
    if 'hydrated_tweets_log_72_hrs.txt' in files_list:
        files_list.remove('hydrated_tweets_log_72_hrs.txt')
    if '.DS_Store' in files_list:
        files_list.remove('.DS_Store')
    print files_list

    file = files_list[x]

    try:
        # ***Hydrate file!
        # Convert the file's tweet ids to strings.
        new_file = str(file)
        filename = path + '/' + new_file

        stringy_tweets = tweets_to_list_converter(filename)

        # Hydrate 100 tweets at a time with those ids:
        begin = 0
        for x in range(len(stringy_tweets)/100 + 1):
            print 'step %d of file %s' % (x, new_file)
            end = begin + 100
            try:
                hydrated_tweets = api_request(stringy_tweets[begin:end])
                new_filename = path + '/01_hydrated_tweets_2_hrs/hydrated_2_hrs' + str(x) + ' ' + str(datetime.now()) + new_file
                with open(new_filename, 'w') as a:
                    for element in hydrated_tweets.iteritems():
                        a.write(str(element) + "\n")
                begin += 100
            except:
                print 'EXCEPTION 1'
                logging.exception(Exception)
                time.sleep(delay)
                delay *= 2
                continue
    except:
        print 'EXCEPTION 2'
        continue
    finally:
        if datetime.now() <= cutoff_time:
            t_diff = cutoff_time - datetime.now()
            time_to_cutoff = (t_diff.days * 1440 + t_diff.seconds / 60.0)*60
            print "waiting %d for cutoff time!" % time_to_cutoff
            time.sleep(time_to_cutoff)
