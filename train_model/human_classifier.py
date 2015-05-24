# This script asks a human to classify tweets that the computer said might be
# about danger.

from pymongo import MongoClient

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def get_human_validation(tweet):
    """Asks the user whether the tweet is about danger or not. Returns 1 if user
    says that it IS about danger. Returns 0 otherwise."""

    prompt = 'Hit 1 if this tweet is about danger, hit 0 otherwise:\n\n\n %s\n\n' % tweet
    return int(raw_input(prompt))

# Define mongodb connection stuff and find documents that any of the classifiers
# think might be about danger:

client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!

found = collect.find( {'$and' : [ 
                     {'human_validated':0},
                     { '$or': [ {'model1_pred':1}, {'model2_pred':1}, {'model3_pred':1} ] } 
                     ] } )

# For the documents where at least one of the classifiers predicts the danger,
# have a human rate the tweet: 
for doc in found:
    mongo_id = doc['id']
    tweet_clean = remove_non_ascii(doc['text'])

    doc['human_code'] = get_human_validation(tweet_clean)
    doc['human_validated'] = 1

    collect.update({'_id':mongo_id}, {"$set": doc}, upsert = False)


