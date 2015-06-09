#!/usr/local/bin/python
# This script grabs retweet counts for every tweet from the 2hr hydrated tweets
# file, finds the tweet that the retweet count belongs to in the mongo database,
# and adds the user info into that tweet's mongo doc.

# You must specify the details of where the tweets are, where the log is that
# records which tweets have already been added to the database, and which 
# collection in the database you want to use.

import numpy as np
import ast
import pandas as pd
import ast
import pickle
import os
from pymongo import MongoClient

#           *** DEFINE FUNCTIONS ***

def find_files_to_add_to_database(logfile_dir, log_file, tweets_dir):
    """Looks for files in the tweets_dir that have yet to be added to the mongo
    database. Returns list of files to add."""

    files_to_add_to_mongo = []
    all_tweet_files = os.listdir(tweets_dir)
    try:
        all_tweet_files.remove('.DS_Store')
    except:
        print "There was no .DS_Store file"

    with open(logfile_dir+log_file, 'r') as loggy:
        log_file_tweets = loggy.readlines()
        for possible_tweet_file in all_tweet_files:
            if (str(possible_tweet_file) + '\n') in log_file_tweets:
                pass
            else:
                files_to_add_to_mongo.append(possible_tweet_file)
    return files_to_add_to_mongo

def file_to_tweets(log_file_directory, log_file_name, tweet_file_directory, tweet_file_name):
    """Extracts user data from tweets in file. Returns it for insertion into mongo.
    Also, adds file that has been converted to tweets into the
    mongoed_tweets_log."""
    try:
        with open(tweet_file_directory + tweet_file_name, 'r') as f:
            all_content = f.readlines()
    except Exception as e:
        print e

    just_tweets = ast.literal_eval(all_content[0])[1]

    tweets_with_metainfo = []
    for tweet in just_tweets.items():
        try:
            output = {}
            output['user'] = tweet[1]['user']
            output['temp_tweet_id'] = tweet[1]['id']
            tweets_with_metainfo.append(output)
        except Exception as e:
            print e
            pass

    with open(log_file_directory + log_file_name, 'a') as logfile:
        logfile.write(tweet_file_name + '\n')

    return tweets_with_metainfo


def tweets_to_mongo(list_of_tweets):
    """Takes a list of tweets, finds each one in the mongo database, and adds
    the retweet count and metainfo into its mongo document."""

    for tweet in list_of_tweets:
        try:
            id_num = tweet['temp_tweet_id']
            # Update the tweet's mongo document with the 2hr hydration info:
            collect.update({ '_id' : id_num }, 
                           { '$set' : {
                                       'user' : tweet['user']
                                       } })
        except Exception as e:
            print e
            continue

def run_all(logfile_directory, logfile_name, tweet_files_directory):
    files_to_add_to_mongo = find_files_to_add_to_database(logfile_directory,
                                                          logfile_name, 
                                                          tweet_files_directory)
    for file_to_add in files_to_add_to_mongo:
        try:
            print file_to_add
            tweets_with_metainfo = file_to_tweets(logfile_directory, 
                                                  logfile_name, 
                                                  tweet_files_directory, 
                                                  file_to_add)
            tweets_to_mongo(tweets_with_metainfo)
        except Exception as e:
            print e
            continue
    print "FINISHED RUNNING ALL"


client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

info = {'logfile_directory' : "/Users/ilya/Projects/danger_tweets/train_model/",
        'logfile_name' : '2hr_user_data_mongoed_log.txt',
        'tweet_files_directory': "/Users/ilya/Projects/danger_tweets/remote_machine_data/2_hrs_hydrated_tweets/"
        }

run_all(info['logfile_directory'], 
        info['logfile_name'],
        info['tweet_files_directory'])

