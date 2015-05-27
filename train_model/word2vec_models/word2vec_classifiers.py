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

n_dim = 530
#Initialize model and build vocab
imdb_w2v = Word2Vec(size=n_dim, min_count=3)
imdb_w2v.build_vocab(x_train)

#Train the model over train_reviews (this may take several minutes)
imdb_w2v.train(x_train)

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
imdb_w2v.train(x_test)

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

print 'Test Accuracy: %.2f'%lr.score(test_vecs, y_test)
print 'Test precisionL %2f' % precision_score(y_test, lr.predict(test_vecs))
print 'Test recall %2f' % recall_score(y_test, lr.predict(test_vecs))

# Try a naivebayes classifier
from sklearn.naive_bayes import GaussianNB
nb = GaussianNB()
nb.fit(train_vecs, y_train)

print 'Test Accuracy: %.2f'%nb.score(test_vecs, y_test)
print 'Test precisionL %2f' % precision_score(y_test, nb.predict(test_vecs))
print 'Test recall %2f' % recall_score(y_test, nb.predict(test_vecs))


