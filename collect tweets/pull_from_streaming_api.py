from config import *
from TwitterAPI import TwitterAPI
import time
from datetime import datetime, timedelta
import numpy as np
import signal

# Setup file logging and make sure you're in the script's own directory:
import logging, os
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)
logging.basicConfig(filename='debug_pull_from_streaming_api.log', level=logging.DEBUG)  

# Set script to terminate in x seconds:
signal.alarm(21600)

# ***----SETUP API DETAILS ---- ***

api_details = []
api_details_path = str(current_dir)
with open(api_details_path + '/api_details.txt', 'r') as a:
    info = a.readlines()
    api_details.append(info)
api_details = api_details[0][0].split(',')

consumer_key = api_details[0]
consumer_secret = api_details[1]
access_token_key = api_details[2]
access_token_secret = api_details[3]

#***---- CALL API AND RECORD TWEETS! --- ****

file_location = str(current_dir) + '/collected_original_tweets/'

delay = 8 # seconds

# Cutoff time is the time at which the current file should be completed and 
# the next file should begin. Set filename based on cutoff time.
cutoff_time = datetime.now() + timedelta(minutes = 30)
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
                    raise Exception('Time for new file')
                random_filter = np.random.random()

                # Only print the tweet to the datafile if it's not a retweet 
                # AND only with 1% probability AND it's not a reply tweet.
                if 'retweeted_status' not in item and \
                    random_filter <= .05 and \
                    item['in_reply_to_user_id'] == None:
                    print item['text']
                    output.write(str(item) + "\n")
                delay = max(8, delay/2)

    except Exception as e:
        logging.exception(e)
        # If you ended up here because an hour has passed since the beginning
        # of the old file, update the filename and reconnect to the API.
        if e.message == 'Time for new file':
            cutoff_time = datetime.now() + timedelta(minutes = 30)
            file_name = file_location + str(cutoff_time) + '.txt'
            print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nNext file!' + file_name
        else:
            print "Error"
            print time.ctime()
            print "Waiting " + str(delay) + " seconds"
            time.sleep(delay)
            delay *= 2



