# This script takes a bunch of ngram that might be included in tweets about
# danger and searches for tweets that include them within the mongo database.
import re
from pymongo import MongoClient
import string
# Create ngrams
diseases = ['alzheimers', 'arthritis', 'asthma', 'autism', 'back pain', 'bladder cancer', 
            'bone cancer', 'brain cancer', 'breast cancer', 'brain tumor', 'bronchitis', 
            'acute bronchitis', 'cancer', 'cancers', 'carpal tunnel', 'celiac disease', 
            'cervical cancer', 'crohns disease', 'depression', 'diabetes', 'down syndrome', 
            'dyslexia', 'epilepsy', 'erectile disfunction', 'fybromyalgia', 'flu', 
            'gallstone', 'herpes', 'gout', 'cardiovascular disease', 'hepatitis', 
            'hyperthyrodism', 'hypertension', 'high blood pressure', 'kidney stone', 
            'leukemia', 'liver tumor', 'miscarriage', 'multiple sclerosis', 'obesity', 
            'obsessive compulsive disorder', 'osteoporosis', 'parkinsons', 'pneumonia', 
            'preterm birth', 'psoriasis', 'rosacea', 'schizophrenia', 'sinusitis', 
            'skin cancer', 'smallpox', 'ulcers', 'jaundice']

ngrams = []
for x in diseases:
    ngrams.append('causes ' + x)
    ngrams.append('can cause ' + x)

natural_disasters = ['Natural disasters', 'Severe weather', 'Tornado warning', 
                     'Flood warning', 'windstorm', 'extreme heat', 'hurricane warning', 
                     'hurricane threat', 'tsunami warning', 'tsunami threat']

ngrams.extend(natural_disasters)

scams = ['Scams', 'Is a scam', 'Scam warning', 'Scam alert', 'new scam', 
         'new e-scam', 'don’t fall for', 'scams spreading', 'identity theft',
         'Prevent identity theft']

ngrams.extend(scams)

people = ['Dangerous people', 'There is a gunman', 'Suspicious person', 'Dangerous person', 
          'dangerous man', 'dangerous men']

ngrams.extend(people)

activities = ['Dangerous driving conditions', 'Unsafe driving conditions', 
              'Dangerous road conditions', 'Unsafe road conditions']

ngrams.extend(activities)

# Define functions that you'll use to pre-process each tweet:
def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

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

# Pre-process ngrams:
ngrams = [process_tweet(ngram) for ngram in ngrams]

# Connect to mongo and retrieve a shitload of tweets:

from pymongo import MongoClient
client = MongoClient()
db = client.tweets
collect = db.test_collection #change this be the right collection!
found = collect.find()

counter = 0
tweets_containing_ngrams = []
while found.alive == True:
    counter += 1
    if counter % 100 == 0: print counter
    raw_tweet = found.next()
    tweet = process_tweet(raw_tweet['text'])
    for ngram in ngrams:
        if ngram in tweet:
            tweets_containing_ngrams.append(tweet)


# Exclude tweets about tornadoes and floods:
for x in range(len(tweets_containing_ngrams)):
    if 'flood warning' in tweets_containing_ngrams[x] or 'tornado warning' in tweets_containing_ngrams[x]:
        del tweets_containing_ngrams[x]



