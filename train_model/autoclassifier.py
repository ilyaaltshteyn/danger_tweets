# Whenever this script is started, it grabs all of the new tweets in the collected 
# tweets directory. Several picked classifiers classify these tweets. Then
# the script compares their classifications and throws out duplicates. Then it
# sends danger tweets, along with a small sample of random tweets from the dataset,
# and with their classifications, to a mongo database.

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.naive_bayes import MultinomialNB
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import ast
import pickle
import os

pickle_load = pickle.load(open('nb1.p', 'r'))
pickle_load2 = pickle.load(open('nb2.p', 'r'))
pickle_load3 = pickle.load(open('rf1.p', 'r'))

current_dir = "/Users/ilya/Projects/danger_tweets/collected_on_remote_machine/may_18th/"
tweets_dir = "/Users/ilya/Projects/danger_tweets/collected_on_remote_machine/may_18th/collected_original_tweets/"

def find_files_to_add_to_database(log_file, tweets_dir = tweets_dir):
    """Looks for files in the tweets_dir that have yet to be added to the mongo
    database. Returns list of files to add."""

    files_to_add_to_mongo = []
    all_tweet_files = os.listdir(tweets_dir)
    try:
        del all_tweet_files['.DS_Store']
        del all_tweet_files['01_hydrated_tweets_2_hrs']
        del all_tweet_files['02_hydrated_tweets_72_hrs']
    except:
        pass

    for possible_tweet_file in all_tweet_files:
        if possible_tweet_file in log_file:
            pass
        else:
            files_to_add_to_mongo.append(possible_tweet_file)
    return files_to_add_to_mongo

def name_to_metainfo(name):
    """Takes the filename of an unhydrated tweet and returns an array of metainfo
    about the tweets in that file. This is possible because the filenames 
    contain a bunch of metainfo about when the tweet was collected, etc."""

    metainfo = ['unhydrated_file_num', 'collection_date', 'collection_time']
    splitup = name.split(' ')
    dictionary = dict(zip(metainfo, splitup))
    dictionary['collection_time'] = dictionary['collection_time'][:-4]
    return dictionary

def file_to_tweets(dirname,filename):
    """Takes a filename and creates a complete set of rows from the tweets in 
    the file. It also uses name_to_metainfo to include the metainfo about the
    file that each tweet came from in each row. Returns all rows as dict."""
    f = dirname + filename
    with open(f, 'r') as f:
        tweets_in_this_file = ast.literal_eval(f.readlines()[0])[1]
    tweet_ids = tweets_in_this_file.keys()
    completed_data_rows = []
    for tweet in tweet_ids:
        complete_tweet_info = name_to_metainfo(str(filename))
        try:
            complete_tweet_info['text'] = tweets_in_this_file[tweet]['text']
            complete_tweet_info['id'] = tweets_in_this_file[tweet]['id']
            complete_tweet_info['machine_classified'] = 0
            complete_tweet_info['human_validated'] = 0
            completed_data_rows.append(complete_tweet_info)
        except:
            print "problem with tweet " + str(tweet)
            continue
    return completed_data_rows

def add_tweets_to_mongo(tweets, collection):
    """Runs file_to_tweets on every file in the given directory and puts them
    all into the given mongodb collection, in the tweets collection. Collection
    should be 1 for now, BUT CHANGE IT BEFORE UPLOADING."""
    # Specify collection to put data into:
    if collection == 1:
        collect = db.hydration1

    # Throw tweets into mongo collection:
    for tweet in tweets:
        collect.insert(tweet)


# Set up mongo connection:
client = MongoClient()
db = client.tweets

with open(current_dir + 'tweets_added_to_mongodb.txt', 'a') as log_file:
    files_to_add = find_files_to_add_to_database(log_file)

    for f_to_add in files_to_add:
        all_tweets = file_to_tweets(tweets_dir, f_to_add)
        add_tweets_to_mongo(all_tweets, 1)





