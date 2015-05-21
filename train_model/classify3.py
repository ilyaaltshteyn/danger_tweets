# This script trains some simple classifiers on the original tweets data, then
# runs the classifiers on big data tweets.

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import ast
import pickle

#             ***Read in training data and strip non-ascii chars***
dir =  "/Users/ilya/Projects/danger_tweets/train_model/"
file = "study2_tweets.txt"
with open(dir+file, 'r') as f:
    tweets = f.readlines()

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

danger_codes = [x[0] for x in tweets]
tweets = [x[2:] for x in tweets]
tweets = [remove_non_ascii(x) for x in tweets]

df = pd.concat([pd.DataFrame(danger_codes), pd.DataFrame(tweets)], axis = 1)
df.columns = ['danger', 'tweet']

df['tweet'] = [x.strip() for x in df['tweet']]

#                  ***Set up the training data***

# min_df is ?, stop_words is a list of english words that don't count in there,
# ngram_range is the number of words to include in the combos that are used as
# features.
vectorizer = CountVectorizer(min_df=1, stop_words='english',ngram_range=(0,6))
vectorizer2 = TfidfVectorizer(min_df=1, stop_words='english',ngram_range=(0,6))
X_train = vectorizer.fit_transform(df.tweet)
X_train_tfidf = vectorizer2.fit_transform(df.tweet)
y_train = df.danger


#            ***Read in big tweet data and strip non-ascii chars***
dir = "/Users/ilya/Projects/danger_tweets/collected_on_remote_machine/may_18th/cleaned_data/"
file = "72_hr_tweets.txt"
with open(dir+file, 'r') as f:
    big_tweets = []
    for t in f:
        big_tweets.append(ast.literal_eval(t))

big_tweets_df = pd.DataFrame(big_tweets)
big_test = big_tweets_df['text']
big_test = [remove_non_ascii(x) for x in big_test]

x_big_data = vectorizer.transform(big_test)
x_big_data_tfidf = vectorizer2.transform(big_test)

#             ***Build some simple classifiers and pickle them***

# Naive bayes with Tfidf: with alpha = .3, gets 20/67 hits.

nb = MultinomialNB(alpha = .3)
nb.fit(X_train_tfidf, y_train)
nb_pred = nb.predict(x_big_data_tfidf)

big_tweets_df['nb_prediction'] = nb_pred
nb_danger_guess = big_tweets_df[big_tweets_df.nb_prediction == '1']

print len(nb_danger_guess)
print nb_danger_guess


pickle_dump = {"Model" : nb, "Vectorizer": vectorizer2}
pickle.dump(pickle_dump, open('nb1.p', 'w'))

# Naive bayes with count vectorizer:
nb = MultinomialNB(alpha = 1)
nb.fit(X_train, y_train)
nb_pred = nb.predict(x_big_data)

big_tweets_df['nb_prediction'] = nb_pred
nb_danger_guess = big_tweets_df[big_tweets_df.nb_prediction == '1']

print len(nb_danger_guess)
pickle_dump = {"Model" : nb, "Vectorizer": vectorizer}
pickle.dump(pickle_dump, open('nb2.p', 'w'))



# Random forest
rf = RandomForestClassifier(verbose = 10, max_depth = 250, n_estimators = 100)
rf.fit(X_train_tfidf, y_train)
rf_pred = rf.predict(x_big_data_tfidf)

big_tweets_df['rf_prediction'] = rf_pred
rf_danger_guess = big_tweets_df[big_tweets_df.rf_prediction == '1']

print len(rf_danger_guess)
pickle_dump = {"Model" : rf, "Vectorizer": vectorizer2}
pickle.dump(pickle_dump, open('rf1.p', 'w'))



