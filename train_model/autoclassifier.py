# Grabs tweets from mongo database that haven't been classified yet. Runs
# several classifiers on them, and adds the classifiers' answers to the mongo
# database. For every 100 that it classifies, it goes back and asks a human to
# classify the danger ones and a random sample of the non-danger ones. 

from pymongo import MongoClient
import pickle
import os

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

directory = "/Users/ilya/Projects/danger_tweets/train_model/"

pickle_load = pickle.load(open(directory + 'nb1.p', 'r'))
pickle_load2 = pickle.load(open(directory + 'nb2.p', 'r'))
pickle_load3 = pickle.load(open(directory + 'rf1.p', 'r'))

client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

model1 = pickle_load['Model']
vectorizer1 = pickle_load['Vectorizer']
model2 = pickle_load2['Model']
vectorizer2 = pickle_load2['Vectorizer']
model3 = pickle_load3['Model']
vectorizer3 = pickle_load3['Vectorizer']

found = collect.find({'computer_classified': 0})

for x in range(10):
    try:
        for doc in found:
            try:
                mongo_id = doc['id']
                tweet_clean = remove_non_ascii(doc['text'])

                # Make computerized predictions:
                nb1_prediction = model1.predict(vectorizer1.transform([tweet_clean]))
                nb2_prediction = model2.predict(vectorizer2.transform([tweet_clean]))
                rf1_prediction = model3.predict(vectorizer3.transform([tweet_clean]))
                doc['computer_classified'] = 1

                doc['model1_pred'] = int(nb1_prediction[0])
                doc['model2_pred'] = int(nb2_prediction[0])
                doc['model3_pred'] = int(rf1_prediction[0])
                collect.update({'_id':mongo_id}, {"$set": doc}, upsert = False)
            except:
                continue
    except:
        continue

os.system('say "your auto classifier has finished running"')
