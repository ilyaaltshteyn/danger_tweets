# This script looks for tweets about etsy and ebay, then runs a spam detector on
# them, then writes them to a file.
import tweetPreprocessor
from pymongo import MongoClient
import time
import math
from random import random

# Establish mongo info:
client = MongoClient()
db = client.tweets
collect = db.test_collection
found = collect.find()

etsy_ebay = []
counter = 0
while found.alive == True:
    counter +=1
    if counter % 100 == 0: print counter
    tweet = found.next()
    tweet_processed = tweetPreprocessor.singleTweet(tweet['text'])
    tweet_processed.strip_and_lower()
    if 'etsy' in tweet or 'ebay' in tweet_processed.tweet:
        etsy_ebay.append(tweet)

etsy_ebay_tweets = [tweet['text'] for tweet in etsy_ebay]

e_e = tweetPreprocessor.tweetDatabase(etsy_ebay_tweets)
e_e.common_twitter_handles.extend(['etsy', 'ebay'])
e_e.identify_spam()
e_e.strip_and_lower_spam()
def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

with open('etsy_ebay_spam.txt', 'w') as outfile:
    for x in e_e.spam_tweets_stripped_and_lowered:
        outfile.write(remove_non_ascii(x) + '\n')