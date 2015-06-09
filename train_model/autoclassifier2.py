#!/usr/local/bin/python
# Grabs tweets from mongo database that haven't been classified yet. Runs
# several classifiers on them, and adds the classifiers' answers to the mongo
# database. For every 100 that it classifies, it goes back and asks a human to
# classify the danger ones and a random sample of the non-danger ones. 

from pymongo import MongoClient
import pickle
import os
import re
import string

# Define functions that you'll use to pre-process each tweet:
def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

regex = re.compile('[%s]' % re.escape(string.punctuation))

def punctuation_stripper(s):
    return regex.sub('', s)

def process_tweet(tweet):
    """This function lowercases the tweet and kills any punctuation in it. 
    It also strips surrounding whitespace and converts every character to ascii.
    Returns the processed tweet."""
    output = remove_non_ascii(tweet)
    output = output.lower()
    output = output.strip()
    output = punctuation_stripper(output)
    return output

directory = "/Users/ilya/Projects/danger_tweets/train_model/"

# Load the models and vectorizers in:
pickle_load = pickle.load(open(directory + 'all_models_june5th.p', 'r'))
pickle_load

model1 = pickle_load['model1']['Model']
vectorizer1 = pickle_load['model1']['Vectorizer']
model2 = pickle_load['model2']['Model']
vectorizer2 = pickle_load['model2']['Vectorizer']
model3 = pickle_load['model3']['Model']
vectorizer3 = pickle_load['model3']['Vectorizer']
model4 = pickle_load['model4']['Model']
vectorizer4 = pickle_load['model4']['Vectorizer']

client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!
found = collect.find({'human_code' : 1}).limit(5000)

# Make predictions:
danger_tweets = []
counter = 0
while found.alive == True:
    print counter
    counter +=1
    single_tweet = found.next()
    mongo_id = single_tweet['id']
    tweet_clean = process_tweet(single_tweet['text'])

    # Make predictions:
    model1_prediction = model1.predict(vectorizer1.transform([tweet_clean]))
    model2_prediction = model2.predict(vectorizer2.transform([tweet_clean]))
    model3_prediction = model3.predict(vectorizer3.transform([tweet_clean]))
    model4_prediction = model4.predict(vectorizer4.transform([tweet_clean]))

    single_tweet['computer_classified'] = 1
    single_tweet['round2_model1_pred'] = int(model1_prediction[0])
    single_tweet['round2_model2_pred'] = int(model2_prediction[0])
    single_tweet['round2_model3_pred'] = int(model3_prediction[0])
    single_tweet['round2_model4_pred'] = int(model4_prediction[0])

    if single_tweet['round2_model1_pred'] == 1 | single_tweet['round2_model2_pred'] == 1 | single_tweet['round2_model3_pred'] == 1 | single_tweet['round2_model4_pred'] == 1:
        danger_tweets.append(single_tweet['text'])
        print single_tweet

