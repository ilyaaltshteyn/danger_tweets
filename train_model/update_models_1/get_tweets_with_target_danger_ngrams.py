from pymongo import MongoClient
import tweetPreprocessor
client = MongoClient()
db = client.tweets
collect = db.test_collection

target_ngrams = 

