# This script pulls tweets from twitter by hashtags and keywords.

import ast
import oauth2
import time
import urllib2
import json
import pickle

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/'
#Get api details:
api_details = []
with open(path + 'api_details.txt', 'r') as a:
    info = ast.literal_eval(a.readlines()[0])
    consumer_key = info['consumer_key']
    consumer_secret = info['consumer_secret']
    access_token_key = info['access_token_key']
    access_token_secret = info['access_token_secret']

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

# def url_maker(queries_dict):
#     """Returns twitter query url suffix for hashtags, search phrases and words. 
#     The inputs must be in a dictionary with a key for each search element type.
#     Returns url to be used in twitter query."""

#     if queries_dict['hashtags']:
#         output ='%23' + queries_dict['hashtags'][0] 
#         for hashtag in queries_dict['hashtags'][1:]:
#             output += '+%23' + hashtag

#     for phrase in queries_dict['phrases']:
#         print phrase.split(' ')
#         words = '+%22' + phrase.split(' ')[0]
#         if len(phrase.split(' ')) > 1:
#             for word in phrase.split(' ')[1:]:
#                 words += '%22' + word
#         output += words
#         # output += '%22'
#     print output

def api_request(twitter_query):
    """Takes a list of hashtag queries (the part after search/ when you search
    for the hashtag on twitter.com) and returns tweets with those hashtags. 
    Hashtags in list must be strings."""

    #Create api searcher:
    url = 'https://api.twitter.com/1.1/search/tweets.json' + twitter_query
    params = {
        "oauth_version": "1.0",
        "oauth_nonce": oauth2.generate_nonce(),
        "oauth_timestamp": int(time.time())
    }
    consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth2.Token(key=access_token_key, secret=access_token_secret)
    params["oauth_consumer_key"] = consumer.key
    params["oauth_token"] = token.key

    req = oauth2.Request(method="GET", url=url, parameters=params)
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)
    headers = req.to_header()
    url = req.to_url()
    response = urllib2.Request(url)
    tweets = urllib2.urlopen(response)
    return json.load(tweets)

all_tweets = []
query_elements = '?q="very%20dangerous"%20OR%20"super%20dangerous"%20OR%20%23warning%20OR%20%23alert&src=typd&lang=en&retweet=false'
for x in range(100):
    search_response = api_request(query_elements)
    for x in search_response['statuses']:
        all_tweets.append(x['text'])
    query_elements = search_response['search_metadata']['next_results']

all_tweets = set(all_tweets)
with open('tweets_from_search.txt', 'a') as output:
    for tweet in all_tweets:
        tweet = remove_non_ascii(tweet)
        output.write(tweet + '\n')


