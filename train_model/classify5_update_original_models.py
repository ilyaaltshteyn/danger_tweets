# This script updates the first two naive_bayes models with the new data from
# the first pass of human-coding (where I hand-coded about 1200 tweets)

# Connect to mongo and pull in tweets that each model said were about danger.

from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import text 


client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

# Grab tweets that each model said were about danger:
print collect.count( { 'model1_pred' : 1}) #846
print collect.count( { 'model2_pred' : 1}) #1013

nb1_danger_coded_tweets = collect.find( { 'model1_pred' : 1})
nb2_danger_coded_tweets = collect.find( { 'model2_pred' : 1})

# Grab tweets that all 3 models said were not about danger:
non_danger_tweets = collect.find( { '$and' : [ { 'model1_pred':0 }, 
                                 { 'model2_pred':0 },
                                 { 'model3_pred':0 } ] } )

# Put all tweets that the model said were about danger, along with an equal number 
# of ones that NO model or human said were about danger, into a new list:
def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

nb1_new_tweets = []
nb1_new_tweets_danger = []
for tweet in nb1_danger_coded_tweets:
    nb1_new_tweets.append(tweet['text'])
    nb1_new_tweets_danger.append(tweet['human_code'])

    # nb1_new_tweets.append(non_danger_tweets.next()['text'])
    # nb1_new_tweets_danger.append(0)

nb1_new_tweets = [remove_non_ascii(x).strip() for x in nb1_new_tweets]
nb1_new_tweets_danger = [str(x) for x in nb1_new_tweets_danger]

nb2_new_tweets = []
nb2_new_tweets_danger = []
for tweet in nb2_danger_coded_tweets:
    nb2_new_tweets.append(tweet['text'])
    nb2_new_tweets_danger.append(tweet['human_code'])

    nb2_new_tweets.append(non_danger_tweets.next()['text'])
    nb2_new_tweets_danger.append(0)

nb2_new_tweets = [remove_non_ascii(x).strip() for x in nb2_new_tweets]
nb2_new_tweets_danger = [str(x) for x in nb2_new_tweets_danger]



#  Add old data in there:


dir =  "/Users/ilya/Projects/danger_tweets/train_model/"
file = "study2_tweets.txt"
with open(dir+file, 'r') as f:
    tweets = f.readlines()

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

danger_codes = [x[0] for x in tweets]
danger_codes.extend(nb1_new_tweets_danger)
tweets = [x[2:] for x in tweets]
tweets = [remove_non_ascii(x) for x in tweets]
tweets.extend(nb1_new_tweets)

df = pd.concat([pd.DataFrame(danger_codes), pd.DataFrame(tweets)], axis = 1)
df.columns = ['danger', 'tweet']

df['tweet'] = [x.strip() for x in df['tweet']]

# Lowercase all data, and strip away tweets that are shorter than 10 characters.
# Also kill any punctuation. 
import re
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

df['tweet'] = [process_tweet(x) for x in df.tweet]
# Drop tweets that are shorter than 11 characters:
df = df[df.tweet.map(len) > 10]

# Build vectorizers and vectorize data:
my_additional_stop_words = []
stop_words_file = "/Users/ilya/Projects/danger_tweets/train_model/locations_stop_words.txt"
with open(stop_words_file, 'r') as infile:
    words = infile.readlines()
    for word in words:
        my_additional_stop_words.append(word[:-1])

stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)

count_vectorizer = CountVectorizer(min_df=1, stop_words = stop_words, ngram_range=(0,4))
x_count_vec = count_vectorizer.fit_transform(df.tweet)

tfidf_vectorizer = TfidfVectorizer(min_df=1, stop_words = stop_words,ngram_range=(0,4))
x_tfidf_vec = tfidf_vectorizer.fit_transform(df.tweet)

#               ***Build new models***

# Naive bayes with count vectorizer:
nb1 = MultinomialNB(alpha = 1)
nb1.fit(x_count_vec, df.danger)

# Naive bayes with tfidf vectorizer:
nb2 = MultinomialNB(alpha = .3)
nb2.fit(x_tfidf_vec, df.danger)

# Random forest with tfidf vectorizer:
rf1 = RandomForestClassifier(max_depth = 250, n_estimators = 15)
rf1.fit(x_tfidf_vec, df.danger)

# SVM






