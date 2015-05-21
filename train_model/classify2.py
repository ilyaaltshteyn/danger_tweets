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
import ast
import pickle

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

nb1 = MultinomialNB()
nb1.fit(X_train, train_data.danger)
model_dump = {"Model": nb1, "Vectorizer": vectorizer}
pickle.dump(model_dump, open('nb1.p', 'w'))

def rf(depth):
    rf = RandomForestClassifier(verbose = 10, max_depth = depth, n_estimators = 100)
    rf.fit(X_train, train_data.danger)
    rf_pred = rf.predict(X_test)
    rf_score = rf.score(X_test, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, rf_pred)
    return rf, precision, recall, str(rf_score)

rf1, prec, rec, rf_scor = rf(250)
print prec, rec, rf_scor
pickle_out = {"Model": rf1, "Vectorizer": vectorizer}
pickle.dump(pickle_out, open('rf1.p', 'w'))

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

#               ***Combine datasets to train/test on combined***
df3 = pd.concat([df, df2], axis = 0)

train3, test3 = train_test_split(df3, test_size = .2)

x_train3 = vectorizer.fit_transform(train3.tweet)
x_test3 = vectorizer.transform(test3.tweet)
y_train3 = train3.danger
y_test3 = test3.danger

#               ***Train/test classifier on combined small data***


nb = MultinomialNB(alpha = 0.01)
nb.fit(x_train3, y_train3)
nb_pred = nb.predict(x_test3)
nb_score = nb.score(x_test3, y_test3)
precision, recall, _, _ = precision_recall_fscore_support(y_test3, nb_pred)
print precision, recall, str(nb_score)

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

#          ***Build classifiers on small data, test on big data***

nb = MultinomialNB(alpha = 0.15)
nb.fit(x_train3, y_train3)
nb_pred = nb.predict(x_big_data)

big_tweets_df['nb_prediction'] = nb_pred
nb_danger_guess = big_tweets_df[big_tweets_df.nb_prediction == '1']
print nb_danger_guess
print len(nb_danger_guess)

nb_danger_guess.to_csv(dir+"nb_predicted_danger_5.csv")
