# # This script removes tweets that are extremely similar to each other in order
# # to have a maximally diverse dataset.

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

path = '/Users/ilya/Projects/danger_tweets/manually_find_danger_tweets/find_ngrams_august_2015/'

data = pd.read_csv(path + 'ngram_tweets_hand_coded.csv')

vec = CountVectorizer()
X = vec.fit_transform(data.tweet)

neigh = NearestNeighbors(radius = .2, metric = 'cosine', algorithm = 'brute')
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

print data.tweet[to_drop]

data = data.drop(data.index[to_drop])

data.to_csv()