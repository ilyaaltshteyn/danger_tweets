# This script merges together all 4 sources of training data (the original
# hand-coded tweets from studies 1 and 2, the tweets that the original machine
# learning classifier identified as being about danger and that I then rated,
# and the tweets that were identified as being about danger based on keywords.)
# It then removes very close doubles from these tweets and writes them to a
# master training file.

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

# Read all data in and merge:
path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/train_new_model/'

data1 = pd.read_csv(path + 'study1_tweets.txt', sep = '\t')
data1 = data1[['tweet', 'real_danger']]
data1 ['dataset'] = 1
data1.columns = ['tweet', 'danger', 'dataset']

data2 = pd.read_csv(path + 'study2_tweets.txt', sep = '\t')
data2.columns = ['danger', 'tweet']
data2 ['dataset'] = 2
data2 = data2[['tweet', 'danger', 'dataset']]

data3 = pd.read_csv(path + '1st_round_tweets.csv')
data3 ['dataset'] = 3
data3.columns = ['tweet', 'danger', 'dataset']

data4 = pd.read_csv(path + 'ngram_tweets_hand_coded.csv')
data4 = data4[['tweet', 'dangerous']]
data4 ['dataset'] = 4
data4.columns = ['tweet', 'danger', 'dataset']

frames = [data1, data2, data3, data4]
all_data = pd.concat(frames)

def replace_bad_chars(tweet):
    return ''.join([i if ord(i) < 128 else ' ' for i in tweet])

all_data['clean_tweets'] = all_data.tweet.apply(replace_bad_chars)


# Remove nearly-identical tweets from training set:
vec = CountVectorizer()
X = vec.fit_transform(all_data.clean_tweets)

neigh = NearestNeighbors(radius = .15, metric = 'cosine', algorithm = 'brute')
neigh.fit(X)

distances, indices = neigh.radius_neighbors(X)

to_drop = []
not_to_drop = []
for index in indices:
    if len(index) > 1:
        if index[0] not in to_drop:
            not_to_drop.append(index[0])
        for i in index[1:]:
            if i not in to_drop:
                to_drop.append(i)

for i in set(not_to_drop):
    if i in to_drop:
        del to_drop[to_drop.index(i)]

print all_data.tweet[to_drop]

data = data.drop(data.index[to_drop])

data.to_csv(path + 'ngram_tweets_hand_coded_2.csv', index = False)