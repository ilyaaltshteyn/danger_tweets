import numpy as np
import pandas as pd
import string
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import precision_recall_fscore_support
from sklearn.feature_extraction import text


#             ***Read in data and strip non-ascii chars***
dir =  "/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/"
file = "manual_search_tweets_rated_may_26th.csv"

data = pd.read_csv(dir+file)
data = data.drop(['Unnamed: 0', 'human_coded'], axis = 1)
data.columns = ['tweet', 'danger']

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

data.tweet = [process_tweet(x) for x in data.tweet]

X_train = data.tweet
y_train = data.danger


# Add the searched-for words and hashtags to stop words:
my_stop_words = ['very dangerous', 'super dangerous', 'warning', 'alert']
updated_stop_words = text.ENGLISH_STOP_WORDS.union(my_stop_words)

vectorizer = CountVectorizer(min_df = 1, stop_words = updated_stop_words, 
                             ngram_range = (0,6))

X_train_count_vec = vectorizer.fit_transform(X_train)


# Build classifiers:

nb1 = MultinomialNB()
nb1.fit(X_train_count_vec, y_train)

rf1 = RandomForestClassifier(max_depth = 250, n_estimators = 20)
rf1.fit(X_train_count_vec, y_train)

def models_predict(tweet):
    tweet = remove_non_ascii(tweet).strip()
    nb1_pred = nb1.predict(vectorizer.transform([tweet]))

    # rf1_pred = rf1.predict(vectorizer.transform([tweet]))
    return nb1_pred #rf1_pred

# Connect to mongo and use a subset of 50k tweets to further train the nb 
# classifier.
from pymongo import MongoClient
client = MongoClient()
db = client.tweets
collect = db.test_collection

tweets = collect.find( { 'computer_classified' : 0 } )

counter = 0
danger_tweets = []
for tweet in tweets:
    counter += 1
    if counter % 100 == 0:
        print counter
    if counter == 100000: break
    if models_predict(tweet['text'])[0] == 1:
        danger_tweets.append(tweet['text'])



