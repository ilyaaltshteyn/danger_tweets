#!/usr/local/bin/python
# This script grabs all unhydrated tweets and throws them into a mongo database.
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

def name_to_metainfo(tweetfile_directory, tweetfile_name):
    """Takes the filename of an unhydrated tweet and returns an array of metainfo
    about the tweets in that file. This is possible because the filenames 
    contain a bunch of metainfo about when the tweet was collected, etc."""
    try:
        name = tweetfile_directory + tweetfile_name
        metainfo = ['unhydrated_file_num', 'collection_date', 'collection_time']
        splitup = tweetfile_name.split(' ')
        dictionary = dict(zip(metainfo, splitup))
        dictionary['unhydrated_file_num'] = dictionary['unhydrated_file_num'][-4:]
        dictionary['collection_time'] = dictionary['collection_time'][:-4]
        dictionary['computer_classified'] = 0
        dictionary['human_validated'] = 0
        return dictionary
    except Exception as e:
        print e
        return {}

def file_to_tweets(log_file_directory, log_file_name, tweet_file_directory, tweet_file_name):
    """Turns filename into metainfo using name_to_metainfo and extracts tweets
    from the file. Returns all this as a single document, for insertion into
    mongo database. Also, adds file that has been converted to tweets into the
    mongoed_tweets_log."""
    try:
        metainfo = name_to_metainfo(tweet_file_directory, tweet_file_name)
        with open(tweet_file_directory + tweet_file_name, 'r') as f:
            all_content = f.readlines()

        tweets_with_metainfo = []
    except Exception as e:
        print e

    for tweet in all_content:
        try:
            output = metainfo.copy()
            output.update(ast.literal_eval(tweet))
            output['_id'] = output['id']
            tweets_with_metainfo.append(output)
        except Exception as e:
            print e
            continue

    with open(log_file_directory + log_file_name, 'a') as logfile:
        logfile.write(tweet_file_name + '\n')

    return tweets_with_metainfo


def tweets_to_mongo(list_of_tweets_as_dicts):
    """Takes a list of tweets as dictionaries and places them into a mongo db
    as separate documents."""

    for tweet in list_of_tweets_as_dicts:
        try:
            collect.insert(tweet)
        except Exception as e:
            print e

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
    
    os.system('say "your first program has finished"')


client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

info = {'logfile_directory' : "/Users/ilya/Projects/danger_tweets/train_model/",
        'logfile_name' : 'mongoed_tweets_log.txt',
        'tweet_files_directory': "/Users/ilya/Projects/danger_tweets/remote_machine_data/raw_original_tweets/"
        }

run_all(info['logfile_directory'], 
        info['logfile_name'],
        info['tweet_files_directory'])

