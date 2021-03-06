# This script updates the first naive_bayes model with the new data from
# the first pass of human-coding (where I hand-coded about 1200 tweets)

# Connect to mongo and pull in tweets that each model said were about danger.

from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import text 
from sklearn.metrics import precision_recall_fscore_support
from sklearn.cross_validation import train_test_split

client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

# Count tweets that each model said were about danger:
print collect.count( { 'model1_pred' : 1}) #846
print collect.count( { 'model2_pred' : 1}) #1013
print collect.count( { 'model3_pred' : 1}) #314
print collect.count( { '$or' : [ 
                    { 'model1_pred' : 1},
                    { 'model2_pred' : 1},
                    { 'model3_pred' : 1}] }) #1210

# How well did each model do?
print collect.count( { '$and' : [
                     { 'model1_pred' : 1},
                     { 'human_code' : 1} ] } ) #185/846 = .21
print collect.count( { '$and' : [
                     { 'model2_pred' : 1},
                     { 'human_code' : 1} ] } ) #200/1013 = .20
print collect.count( { '$and' : [
                     { 'model3_pred' : 1},
                     { 'human_code' : 1} ] } ) #160/314 = .51


nb1_danger_coded_tweets = collect.find( { '$or' : [ 
                    { 'model1_pred' : 1},
                    { 'model2_pred' : 1},
                    { 'model3_pred' : 1}] })

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

    # Append two non-danger tweets for every possibly-danger tweet:
    nb1_new_tweets.append(non_danger_tweets.next()['text'])
    nb1_new_tweets_danger.append(0)
    nb1_new_tweets.append(non_danger_tweets.next()['text'])
    nb1_new_tweets_danger.append(0)


nb1_new_tweets = [remove_non_ascii(x).strip() for x in nb1_new_tweets]
nb1_new_tweets_danger = [str(x) for x in nb1_new_tweets_danger]


#  Add old data to nb1 tweets:
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
import re, string
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


# Train-test split the data:

def cross_val_nb1(ngram_low, ngram_high, alpha, which_stop_words):
    """Used for cross-validating and testing hyperparameters of a naive bayes
    model with a count vectorizer."""

    if which_stop_words ==1:
        stop_words = my_additional_stop_words
    else:
        stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)

    x_train, x_test, y_train, y_test = train_test_split(df.tweet, df.danger)

    count_vectorizer = CountVectorizer(min_df=1, stop_words = stop_words, ngram_range=(ngram_low,ngram_high))
    x_train_count_vec = count_vectorizer.fit_transform(x_train)
    x_test_count_vec = count_vectorizer.transform(x_test)

    # Naive bayes with count vectorizer:
    nb1 = MultinomialNB(alpha = alpha)
    nb1.fit(x_train_count_vec, y_train)
    nb_pred = nb1.predict(x_test_count_vec)
    # nb_score = nb1.score(x_test_count_vec, y_test)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, nb_pred)

    return precision[1], recall[1]

# print cross_val_nb1(0,2,1,0)

ngram_low_vals = [0,1,2]
ngram_hi_vals = [2,5]
alpha = [.5, 1, 2]
which_stop_words = [1,2]
precisions = []
accuracies = []

# Cross validate, testing for the effects of all of those variables above:
for a in ngram_low_vals:
    for b in ngram_hi_vals:
        for c in alpha:
            for d in which_stop_words:
                print a, b, c, d
                precision = 0
                accuracy = 0
                for i in range(5):
                    prec, acc = cross_val_nb1(a,b,c,d)
                    precision += prec
                    accuracy += acc
                precisions.append((a,b,c,d,precision/5))
                accuracies.append((a,b,c,d,accuracy/5))

from matplotlib import pyplot as plt
import seaborn as sns
sns.set(style = 'whitegrid')
import numpy as np
xs = range(len(precisions))
plt.plot(xs, [x[4] for x in precisions], label = "Precision")
plt.plot(xs, [x[4] for x in accuracies], label = "Recall")
plt.legend(fontsize = 14)
plt.xticks(xs)
plt.xlabel('Hyperparameter combo number', fontsize = 14)
plt.ylabel('Performance', fontsize = 14)
plt.title("Optimizing precision/recall tradeoff of a naive bayes classifier for identifying danger tweets", fontsize = 15)
sns.despine()
plt.show()

for x in range(len(precisions)):
    print precisions[x], accuracies[x]
# The ideal count vectorizer models have this performance for precision and recall, with these hyperparameters:
# Model 1:
# 0(0, 5, 0.5, 2, 0.73) (0, 5, 0.5, 2, 0.84)
# Those hyperparameters are:
# ngram_low_vals = [0]
# ngram_hi_vals = [5]
# alpha = [.5]
# which_stop_words = [2] (all of them!)


# Model 2:
# 2(0, 2, 1, 1, 0.94473621934186391) (0, 2, 1, 1, 0.60729764887849147)
# Those hyperparameters are:
# ngram_low_vals = [0]
# ngram_hi_vals = [2]
# alpha = [1]
# which_stop_words = [1]

# Now do the same thing but for a tfidf vectorizer (model nb2):

def cross_val_nb2(ngram_low, ngram_high, alpha, which_stop_words):
    """Used for cross-validating and grid searching hyperparameters for a naive
    bayes classifier with a tfidf vectorizer."""

    if which_stop_words == 1:
        stop_words = my_additional_stop_words
    else:
        stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)

    x_train, x_test, y_train, y_test = train_test_split(df.tweet, df.danger)
    
    tfidf_vectorizer = TfidfVectorizer(min_df=1, stop_words = stop_words, ngram_range=(ngram_low,ngram_high))
    x_train_tfidf_vec = tfidf_vectorizer.fit_transform(x_train)
    x_test_tfidf_vec = tfidf_vectorizer.transform(x_test)

    # Naive bayes with tfidf vectorizer:
    nb2 = MultinomialNB(alpha = alpha)
    nb2.fit(x_train_tfidf_vec, y_train)
    nb_pred = nb2.predict(x_test_tfidf_vec)
    precision, recall, _, _ = precision_recall_fscore_support(y_test, nb_pred)

    return precision[1], recall[1]

# print cross_val_nb1(0,2,1,0)

ngram_low_vals = [0,1]
ngram_hi_vals = [2,5]
alpha = [.15, .3, .5, .75]
which_stop_words = [1,2]
precisions_nb2 = []
recalls_nb2 = []

# Cross validate, testing for the effects of all of those variables above:
for a in ngram_low_vals:
    for b in ngram_hi_vals:
        for c in alpha:
            for d in which_stop_words:
                print a, b, c, d
                precision = 0
                recall = 0
                for i in range(5):
                    prec, rec = cross_val_nb2(a,b,c,d)
                    precision += prec
                    recall += rec
                precisions_nb2.append((a,b,c,d,precision/5))
                recalls_nb2.append((a,b,c,d,recall/5))

xs = range(len(precisions_nb2))
plt.plot(xs, [x[4] for x in precisions_nb2], label = "Precision")
plt.plot(xs, [x[4] for x in recalls_nb2], label = "Recall")
plt.legend(fontsize = 14)
plt.xticks(xs)
plt.xlabel('Hyperparameter combo number', fontsize = 14)
plt.ylabel('Performance', fontsize = 14)
plt.title("Optimizing precision/recall tradeoff of a naive bayes classifier with tfidf vectorizer for identifying danger tweets", fontsize = 15)
sns.despine()
plt.show()

for x in range(len(precisions)):
    print precisions_nb2[x], recalls_nb2[x]
# The ideal tfidf models have this precision/recall, with these hyperparameters:
# 8, (0, 5, 0.15, 1, 0.95551887174468342) (0, 5, 0.15, 1, 0.56277806992555335)
# 16,(1, 2, 0.15, 1, 0.87443407215339275) (1, 2, 0.15, 1, 0.71733605619063101)
# ngram_low_vals = [0] and [1]
# ngram_hi_vals = [5] and [2]
# alpha = [.15] and [.15]
# which_stop_words = [1](my custom ones) and [1]


# Now build the 4 models you chose above, and pickle:
import pickle
all_models = {}

# Read in custom stop words list:
my_additional_stop_words = []
stop_words_file = "/Users/ilya/Projects/danger_tweets/train_model/locations_stop_words.txt"
with open(stop_words_file, 'r') as infile:
    words = infile.readlines()
    for word in words:
        my_additional_stop_words.append(word[:-1])


#  ***BUILD MODEL ONE:
# Count vectorizer, ngram_low_vals = [0], ngram_hi_vals = [5], alpha = [.5], 
# using all of the stop words (mine + others)
all_stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)
count_vectorizer = CountVectorizer(min_df=1, stop_words = all_stop_words, 
                                   ngram_range=(0,5))
x_all_count_vec = count_vectorizer.fit_transform(df.tweet)

nb1_countvect = MultinomialNB(alpha = .5)
nb1_countvect.fit(x_all_count_vec, df.danger)

all_models['model1'] = {'Vectorizer' : count_vectorizer,
                      'Model' : nb1_countvect}


#  ***BUILD MODEL TWO:
# Count vectorizer, ngram_low_vals = [2], ngram_hi_vals = [5], alpha = [2],
# using my custom stop words.

count_vectorizer_nb2 = CountVectorizer(min_df=1, stop_words = my_additional_stop_words, 
                                   ngram_range=(0,2))
x_all_countvect_nb2 = count_vectorizer_nb2.fit_transform(df.tweet)

nb2_countvect = MultinomialNB(alpha = 1)
nb2_countvect.fit(x_all_countvect_nb2, df.danger)

all_models['model2'] = {'Vectorizer' : count_vectorizer_nb2,
                      'Model' : nb2_countvect}


#  ***BUILD MODEL THREE:
# Tfidf vectorizer, ngram_low_vals = [0], ngram_hi_vals = [2], alpha = [.3]
# using my custom stop words.

tfidf_vectorizer_nb3 = TfidfVectorizer(min_df=1, stop_words = my_additional_stop_words, 
                                       ngram_range=(0, 5))
x_all_tfidfvect_nb3 = tfidf_vectorizer_nb3.fit_transform(df.tweet)

nb3_tfidfvect = MultinomialNB(alpha = .15)
nb3_tfidfvect.fit(x_all_tfidfvect_nb3, df.danger)

all_models['model3'] = {'Vectorizer' : tfidf_vectorizer_nb3,
                      'Model' : nb3_tfidfvect}


#  ***BUILD MODEL FOUR:
# Tfidf vectorizer, ngram_low_vals = [1], ngram_hi_vals = [5], alpha = [.15],
# using my custom stop words ALONG WITH the scikit standard stop words.

tfidf_vectorizer_nb4 = TfidfVectorizer(min_df=1, stop_words = my_additional_stop_words, 
                                       ngram_range=(1, 2))
x_all_tfidfvect_nb4 = tfidf_vectorizer_nb4.fit_transform(df.tweet)

nb4_tfidfvect = MultinomialNB(alpha = .15)
nb4_tfidfvect.fit(x_all_tfidfvect_nb4, df.danger)

all_models['model4'] = {'Vectorizer' : tfidf_vectorizer_nb4,
                      'Model' : nb4_tfidfvect}

with open('/Users/ilya/Projects/danger_tweets/train_model/all_models_june5th.p', 'wb') as pickleout:
    pickle.dump(obj = all_models, file = pickleout)
