import numpy as np
from sklearn.cross_validation import train_test_split
from gensim.models.word2vec import Word2Vec
from sklearn.metrics import precision_score, recall_score

path = "/Users/ilya/Projects/danger_tweets/train_model/word2vec_models/"

with open('danger_tweets_only.txt', 'r') as infile:
    pos_tweets = infile.readlines()

with open('non_danger_tweets_only.txt', 'r') as infile:
    neg_tweets = infile.readlines()

#use 1 for positive sentiment, 0 for negative
y = np.concatenate((np.ones(len(pos_tweets)), np.zeros(len(neg_tweets))))

x_train, x_test, y_train, y_test = train_test_split(np.concatenate((pos_tweets, neg_tweets)), y, test_size=0.2)

#Do some very minor text preprocessing
def cleanText(corpus):
    corpus = [z.lower().replace('\n','').split() for z in corpus]
    return corpus


x_train = cleanText(x_train)
x_test = cleanText(x_test)

n_dim = 300

#                   ***Read in big tweets data***
import ast
import pandas as pd
dir = "/Users/ilya/Projects/ilya@first_remote_computer/collected_on_remote_machine/may_18th/cleaned_data/"
file = "72_hr_tweets.txt"
with open(dir+file, 'r') as f:
    big_tweets = []
    for t in f:
        big_tweets.append(ast.literal_eval(t))

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])
big_tweets_df = pd.DataFrame(big_tweets)
big_test = big_tweets_df['text']
big_test = [remove_non_ascii(x) for x in big_test]

#Initialize GoogleNews model:
imdb_w2v = Word2Vec.load_word2vec_format(path + 'google_data/GoogleNews-vectors-negative300.bin', binary=True)

#Build word vector for training set by using the average value of all word vectors in the tweet, then scale
def buildWordVector(text, size):
    vec = np.zeros(size).reshape((1, size))
    count = 0.
    for word in text:
        try:
            vec += imdb_w2v[word].reshape((1, size))
            count += 1.
        except KeyError:
            continue
    if count != 0:
        vec /= count
    return vec

from sklearn.preprocessing import scale
train_vecs = np.concatenate([buildWordVector(z, n_dim) for z in x_train])
train_vecs = scale(train_vecs)

#Train word2vec on test tweets
# imdb_w2v.train(x_test)

#Build test tweet vectors then scale
test_vecs = np.concatenate([buildWordVector(z, n_dim) for z in x_test])
test_vecs = scale(test_vecs)

# Use classification algorithm (i.e. Stochastic Logistic Regression) on training set, then assess model performance on test set
from sklearn.linear_model import SGDClassifier
scores = []
precision_scores=[]
recall_scores=[]
for x in range(10):
    print x
    lr = SGDClassifier(loss='log', penalty='l1')
    lr.fit(train_vecs, y_train)
    scores.append(lr.score(test_vecs, y_test))
    precision_scores.append(precision_score(y_test, lr.predict(test_vecs)))
    recall_scores.append(recall_score(y_test, lr.predict(test_vecs)))

print "accuracy: %f" % np.mean(scores)
print "precision: %f" % np.mean(precision_scores)
print "recall_scores: %f" % np.mean(recall_scores)

# Try a naivebayes classifier
from sklearn.naive_bayes import GaussianNB

scores = []
precision_scores=[]
recall_scores=[]
for x in range(10):
    print x
    nb = GaussianNB()
    nb.fit(train_vecs, y_train)
    scores.append(lr.score(test_vecs, y_test))
    precision_scores.append(precision_score(y_test, lr.predict(test_vecs)))
    recall_scores.append(recall_score(y_test, lr.predict(test_vecs)))

print "accuracy: %f" % np.mean(scores)
print "precision: %f" % np.mean(precision_scores)
print "recall_scores: %f" % np.mean(recall_scores)

# Try out the above classifier on the big tweets data
test_vecs = np.concatenate([buildWordVector(z, n_dim) for z in big_test])
test_vecs = scale(test_vecs)
output = nb.predict(test_vecs)
output = pd.Series(output)
predicted_danger_tweets = []
for k, v in enumerate(output):
    if v == True:
        predicted_danger_tweets.append(big_test[k])

output = nb.predict_proba(test_vecs)
output = pd.Series(output)
predicted_proba_danger_tweets = []
for k, v in enumerate(output):
    if v[0] > .999:
        predicted_proba_danger_tweets.append(big_test[k])

# Try out the linear regression classifier on the big tweets data:
test_vecs = np.concatenate([buildWordVector(z, n_dim) for z in big_test])
test_vecs = scale(test_vecs)
output = lr.predict(test_vecs)
output = pd.Series(output)
predicted_danger_tweets = []
for k, v in enumerate(output):
    if v == True:
        predicted_danger_tweets.append(big_test[k])

output = lr.predict_proba(test_vecs)
output = pd.Series(output)
predicted_proba_danger_tweets = []
for k, v in enumerate(output):
    if v[0] > .999:
        predicted_proba_danger_tweets.append(big_test[k])


