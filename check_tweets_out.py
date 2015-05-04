# This script pulls retweets for each tweet 2 hours after it is tweeted, and then again 24 hours after it is tweeted.

# ----****** FIRST, CREATE THE API CALLER *****------

import oauth2, time, urllib2, json, logging, signal

# Setup file logging and make sure you're in the script's own directory:
import logging, os
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)
logging.basicConfig(filename='debug_check_tweets.log', level=logging.DEBUG)  

# Make it so the script dies after a certain amount of time, and sleeps before
# starting so it's properly synced with pull_from_streaming_api.py
signal.alarm(22600)
time.sleep(3700)

path = str(current_dir) +'/collect tweets/'

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



# ----****** DEFINE FUNCTIONS THAT WILL PRODUCE LISTS OF TWEETS *****----

import ast
from os import listdir


def file_collector(path):
    """Checks which files of tweets have not yet been hydrated.
    Returns list of files that still need to be hydrated."""
    with open(path + '/hydrated_tweets_log.txt', 'r') as c:
        hydrated = c.readlines()
        files = [x for x in listdir(path) if (x + '\n') not in hydrated]
    return files

def logger(path, filename):
    """Adds the name of a given file to the log of hydrated tweets files."""
    with open(path + '/hydrated_tweets_log.txt', 'a') as file:
        file.write(filename + '\n')

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



# ----**** NOW ACTUALLY RUN ALL THOSE FUNCTIONS TO GET HYDRATED DATA! ***---

import time
path = str(current_dir) + '/collect tweets/collected_original_tweets/'

# Create the log:
with open(path + '/hydrated_tweets_log.txt', 'w') as create_log:
    pass

while True:
    try:
        # Get list of tweet files that still need to be hydrated:
        files_list = file_collector(path)

        # Remove some files from the list that are not data files:
        files_list.remove('hydrated_tweets')
        files_list.remove('hydrated_tweets_log.txt')

        # Check to see if there is more than one tweets file. If there is not, 
        # then wait an hour. This ensures that only completed tweets files get 
        # hydrated.
        if len(files_list) < 4:
            time.sleep(1800)
            print 'Sleeping to wait for new files'

        # If there are enough files in files list, loop through them and hydrated
        # their tweets:
        for new_file in files_list[1:]:
            print new_file
            # Take the first file in the list and convert its tweet ids to strings.
            filename = path + new_file
            stringy_tweets = tweets_to_list_converter(filename)
            # Hydrate 100 tweets at a time with those ids:
            begin = 0
            for x in range(len(stringy_tweets)/100 + 1):
                print 'step %d of file %s' % (x, new_file)
                end = begin + 100
                try:
                    hydrated_tweets = api_request(stringy_tweets[begin:end])
                    new_filename = path + '/hydrated_tweets/hydrated' + str(x) + ' ' + new_file
                    with open(new_filename, 'w') as a:
                        for element in hydrated_tweets.iteritems():
                            a.write(str(element) + "\n")
                    begin += 100
                except:
                    logging.exception(Exception)
                    time.sleep(1800)
                    continue

            # Add the current file to the log:
            logger(path, new_file)

    except:
        logging.exception(Exception)
        time.sleep(1800)
        continue