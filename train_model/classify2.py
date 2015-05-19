from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

#             ***Read in data and strip non-ascii chars***
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

#                          ***Train-test split***

train_data, test_data = train_test_split(df, test_size = .2)

# min_df is ?, stop_words is a list of english words that don't count in there,
# ngram_range is the number of words to include in the combos that are used as
# features.
vectorizer = CountVectorizer(min_df=1, stop_words='english',ngram_range=(0,6))

X_train = vectorizer.fit_transform(train_data.tweet)
X_test = vectorizer.transform(test_data.tweet)
y_train = train_data.danger
y_test = test_data.danger


#                    ***Build some simple classifiers***

def naive_bayes():
    nb = MultinomialNB()
    nb.fit(X_train, train_data.danger)
    nb_pred = nb.predict(X_test)
    nb_score = nb.score(X_test, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, nb_pred)
    return precision, recall, str(nb_score)

prec, rec, scor = naive_bayes()
print "Precision is %r, recall is %r, accuracy is %r" % (prec, rec, scor)

def rf(depth):
    rf = RandomForestClassifier(verbose = 10, max_depth = depth, n_estimators = 100)
    rf.fit(X_train, train_data.danger)
    rf_pred = rf.predict(X_test)
    rf_score = rf.score(X_test, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, rf_pred)
    return precision, recall, str(rf_score)

# Try different values of max_depth for the random forest:

params = [50,100,150,200,250,300,350,400]

precisions = []
recalls = []
for depth in params:
    prec, rec, _ = rf(depth)
    precisions.append(prec[1]) #note it's only the precision for danger tweets
    recalls.append(rec[1])

prec, rec, scor = rf()
print "Precision is %r, recall is %r, accuracy is %r" % (prec, rec, scor)

plt.plot(params,precisions)
plt.plot(params, recalls)
plt.axis([0,410,0,1])
plt.legend()
plt.show()


#                   ***Read in new tweet data***

dir =  "/Users/ilya/Projects/danger_tweets/train_model/"
file = "study1_tweets.txt"
with open(dir+file, 'r') as f:
    tweets2 = f.readlines()

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

danger_codes2 = [x[0] for x in tweets2]
tweets2 = [x[2:] for x in tweets2]
tweets2 = [remove_non_ascii(x) for x in tweets2]

df2 = pd.concat([pd.DataFrame(danger_codes2), pd.DataFrame(tweets2)], axis = 1)
df2.columns = ['danger', 'tweet']

df2['tweet'] = [x.strip() for x in df2['tweet']]

df2 = df2[df2.index > 0]

X_test2 = vectorizer.transform(df2.tweet)
y_test2 = df2.danger

#                   ***Test classifier on new data***

# Build classifier based on old data:

rf = RandomForestClassifier(verbose = 10, max_depth = 250, n_estimators = 100)
rf.fit(X_train, train_data.danger)

rf_pred2 = rf.predict(X_test2)
rf_score2 = rf.score(X_test2, y_test2)
precision2, recall2, _, _ = precision_recall_fscore_support(y_test2, rf_pred2)
print precision2, recall2, str(rf_score2)


