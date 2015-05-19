from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
import numpy as np
import pandas as pd

#             ***Read in data and strip non-ascii chars***
file = "tweets_as_text.txt"
dir =  "/Users/ilya/Projects/danger_tweets/train_model/"
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



train_data, test_data = train_test_split(df, test_size = .2)

# min_df is ?, stop_words is a list of english words that don't count in there,
# ngram_range is the number of words to include in the combos that are used as
# features.
vectorizer = CountVectorizer(min_df=1, stop_words='english',ngram_range=(0,6))

X_train = vectorizer.fit_transform(train_data.tweet)
X_test = vectorizer.transform(test_data.tweet)
y_train = train_data.danger
y_test = test_data.danger


"""standard imports"""
from sklearn.naive_bayes import MultinomialNB

def naive_bayes():
    nb = MultinomialNB()
    nb.fit(X_train, train_data.danger)
    nb_pred = nb.predict(X_test)
    nb_score = nb.score(X_test, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, nb_pred)
    return precision, recall, str(nb_score)

prec, rec, scor = naive_bayes()
print "Precision is %r, recall is %r, accuracy is %r" % (prec, rec, scor)

def rf():
    rf = RandomForestClassifier(verbose = 10)
    rf.fit(X_train, train_data.danger)
    rf_pred = rf.predict(X_test)
    rf_score = rf.score(X_test, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, rf_pred)
    return precision, recall, str(rf_score)

prec, rec, scor = rf()
print "Precision is %r, recall is %r, accuracy is %r" % (prec, rec, scor)






