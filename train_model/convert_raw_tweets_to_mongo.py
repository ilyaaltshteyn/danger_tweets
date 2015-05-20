# The idea here is to specify a directory of tweets and have all the tweets
# be loaded into a Mongo database. But to only load the relevant info, that 
# being the tweet itself, its origin time, and its retweets at each of the two
# hydration points.

import os
import ast
from pymongo import MongoClient

#           ***FUNCTIONS TO PULL DATA OUT OF RAW DATAFILES***

metainfo = ['hydration_point', 'hydration_filenum', 'hydration_date', 'hydration_time',
            'unhydrated_file_num', 'origin_date', 'origin_time']

def name_to_metainfo(name):
    """Takes the filename of a hydrated tweet and returns an array of metainfo
    about the tweets in that file. This is possible because the filenames 
    contain a bunch of metainfo about when the tweet was collected, etc."""

    splitup = name.split(' ')
    dictionary = dict(zip(metainfo, splitup))
    dictionary['origin_time'] = dictionary['origin_time'][:-4]
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
            complete_tweet_info['favorites'] = tweets_in_this_file[tweet]['favorite_count']
            complete_tweet_info['reply'] = tweets_in_this_file[tweet]['in_reply_to_screen_name']
            complete_tweet_info['retweets'] = tweets_in_this_file[tweet]['retweet_count']
            complete_tweet_info['followers_count'] = tweets_in_this_file[tweet]['user']['followers_count']
            completed_data_rows.append(complete_tweet_info)
        except:
            print "problem with tweet " + str(tweet)
            continue
    return completed_data_rows


#                      ***THROW TWEETS INTO MONGO DB***

dir = "/Users/ilya/Projects/danger_tweets/collected_on_remote_machine/may_18th/collected_original_tweets/01_hydrated_tweets_2_hrs/"
name = "hydrated_2_hrs 1 2015-05-14 05:05:53.098370 0287 2015-05-14 03:29:27.141734.txt"

# Set up mongo connection:
client = MongoClient()
db = client.tweets

def directory_to_mongo(directory, collection):
    """Runs file_to_tweets on every file in the given directory and puts them
    all into the given mongodb collection, in the tweets collection. Collection
    should be either 1 (for the tweets hydrated at 2 hrs) or 2 (for the ones
    hydrated at 72 hours)."""
    # Specify collection to put data into:
    if collection == 1:
        collect = db.hydration1
    if collection == 2:
        collect = db.hydration2

    files = os.listdir(directory)
    for f in files[1:]:
        print f
        tweets = file_to_tweets(directory, f)
        # Throw tweets into mongo collection:
        for tweet in tweets:
            collect.insert(tweet)

directory_to_mongo(dir, 1)


