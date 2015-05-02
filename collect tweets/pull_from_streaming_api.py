from config import *
from TwitterAPI import TwitterAPI
import time
from datetime import datetime, timedelta
import numpy as np

consumer_key = 'PYD3Vu4GLJ88SSUti2aRK8GNH'
consumer_secret = 'lWb4RLVrqnFL7xgYszkjKWeHlNWhlgA3Rerv4mBXB0ukc6kJdO'
access_token_key = '2289200166-jHIq4sAHm75R9ijQ4TM8nkBarRw3ZeCo0ipSLwA'
access_token_secret = '5ivDgreVyAUIIxJeb00CUBeGLjYt7XYhdmfyB0dTn70ae'
file_location = '/Users/ilya/Projects/danger_tweets/collect tweets/'

delay = 8 # seconds

# Cutoff time is the time at which the current file should be completed and 
# the next file should begin. Set filename based on cutoff time.
cutoff_time = datetime.now() + timedelta(hours = 1)
file_name = file_location + str(cutoff_time) + '.txt'

while True:
    try:
        api = TwitterAPI(consumer_key, consumer_secret,
                         access_token_key, access_token_secret)
        r = api.request('statuses/sample', {'country':'United States',
            'language' : 'en'})
        with open(file_name, "a") as output:
            for item in r.get_iterator():
                
                # If 1 hour has passed since the beginning of the file, then
                # send script to the exception that updates the filename.
                if datetime.now() > cutoff_time:
                    raise ValueError('Time for new file')
                random_filter = np.random.random()

                # Only print the tweet to the datafile if it's not a retweet 
                # AND only with 1% probability.
                if 'retweeted_status' not in item and random_filter <= .01:
                    print item
                    output.write(str(item) + "\n")
                delay = max(8, delay/2)

    except Exception as e:
        
        # If you ended up here because an hour has passed since the beginning
        # of the old file, update the filename and reconnect to the API.
        if e.message == 'Time for new file':
            cutoff_time = datetime.now() + timedelta(seconds = 5)
            file_name = file_location + str(cutoff_time) + '.txt'
            print 'Next file!' + file_name
        else:
            print "Error"
            print time.ctime()
            print "Waiting " + str(delay) + " seconds"
            time.sleep(delay)
            delay *= 2

cutoff_time = datetime.now() + timedelta(minutes = 1)
file_name = file_location + str(cutoff_time) + '.txt'



