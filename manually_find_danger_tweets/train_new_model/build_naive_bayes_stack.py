# This script builds a stack of naive bayes classifiers to figure out what
# constitutes a danger tweet.

import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
import string
from sklearn.metrics import precision_recall_fscore_support

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/train_new_model/'
filename = 'master_train_data.csv'
data = pd.read_csv(path + filename)
data = data[['clean_tweets', 'danger']]

# Set everything up so you can create a sample of data to fit each classifier:

negative = data[data.danger == 0]
positive = data[data.danger == 1]

print 'Negative examples: %d' % len(negative)
print 'Positive examples: %d' % len(positive)

train_pos, test_pos = train_test_split(positive, test_size = .33)
train_neg, test_neg = train_test_split(negative, test_size = .33)

def preprocess(tweets_list):
    """ Lowercases, strips whitespace and punctuation. """
    def do_all(tweet):
        exclude = set(string.punctuation)
        tweet = ''.join(ch for ch in tweet if ch not in exclude)
        return tweet.lower().strip()
    return [do_all(x) for x in tweets_list]

def bootstrap_sample(pos, neg, sample_size = 750):
    """ Samples sample_size datapoints from positive and negative sets, then 
    returns the combined sets as a shuffled dataframe. """

    pos_sample = pos.sample(n = sample_size, replace = True, axis = 0)
    neg_sample = neg.sample(n = sample_size, replace = True, axis = 0)
    all_data = pd.concat([pos_sample, neg_sample])
    all_data = all_data.iloc[np.random.permutation(len(all_data))]

    return all_data

def naive_bayes_builder(pos_train, neg_train, vectorizer):
    """ Takes all of the training data as input. Creates a bootstrapped sample
    of the training data (using boostrap_sample()). Vectorizes the data and
    returns a naive bayes classifier that makes predictions. """

    x_train_text = bootstrap_sample(train_pos, train_neg)
    y_train = x_train_text.pop('danger')
    x_train_text = preprocess(x_train_text.clean_tweets)

    X_train = vectorizer.transform(x_train_text)

    clf = MultinomialNB(class_prior = [.8, .2]).fit(X_train, y_train)

    return clf

def create_test_set(pos_sample, neg_sample, vectorizer):
    """ Creates a complete, vectorized, shuffled test set out of positive and
    negative datapoints. """

    all_data = pd.concat([pos_sample, neg_sample])
    all_data = all_data.iloc[np.random.permutation(len(all_data))]
    test_y = all_data.pop('danger')
    test_x = vectorizer.transform(preprocess(all_data.clean_tweets))
    return test_x, test_y

def create_ensemble(pos_sample, neg_sample, number_of_classifiers, 
                    vectorizer, voting_threshhold, test_x, test_y):
    """ Creates an ensemble of naive bayes classifiers, each one trained on a
    bootstrapped sample of the training data. Returns their accuracy at the
    voting_threshhold, which is the number of classifiers that must vote that a
    given datapoint is positive in order for it to be considered positive. """
    ensemble = []
    for x in range(number_of_classifiers):
        if x % 20 == 0:
            print 'building classifier number %d' % x
        ensemble.append(naive_bayes_builder(pos_sample, neg_sample, vectorizer))

    votes = np.zeros(len(test_y))
    for clf in ensemble:
        votes += clf.predict(test_x)
    
    votes = [1 if x > voting_threshhold else 0 for x in votes]

    print precision_recall_fscore_support(test_y, votes)



vectorizer = HashingVectorizer(decode_error='ignore', n_features=2 ** 18,
                               non_negative = True, ngram_range = (1,1))

test_x, test_y = create_test_set(test_pos, test_neg, vectorizer)

create_ensemble(pos_sample = train_pos, neg_sample = train_neg, 
                number_of_classifiers = 500, vectorizer = vectorizer, 
                voting_threshhold = 250, test_x = test_x, test_y = test_y)

# clf1 = naive_bayes_builder(train_pos, train_neg, vectorizer)


# y_pred = clf1.predict(test_x)

# print precision_recall_fscore_support(test_y, y_pred)
