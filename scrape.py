
from config import *
from TwitterAPI import TwitterAPI
import time

consumer_key = 'PYD3Vu4GLJ88SSUti2aRK8GNH'
consumer_secret = 'lWb4RLVrqnFL7xgYszkjKWeHlNWhlgA3Rerv4mBXB0ukc6kJdO'
access_token_key = '2289200166-jHIq4sAHm75R9ijQ4TM8nkBarRw3ZeCo0ipSLwA'
access_token_secret = '5ivDgreVyAUIIxJeb00CUBeGLjYt7XYhdmfyB0dTn70ae'
file_location = '/Users/ilya/Projects/twitter_danger/out.txt'

delay = 8 # seconds

while True:
    try:
        api = TwitterAPI(consumer_key, consumer_secret,
                         access_token_key, access_token_secret)
        r = api.request('statuses/sample', {'country':'United States',
            'language' : 'en'})
        with open(file_location, "a") as output:
            for item in r.get_iterator():
                print item
                output.write(str(item) + "\n")
                delay = max(8, delay/2)
    except:
        print "Error"
        print time.ctime()
        print "Waiting " + str(delay) + " seconds"
        time.sleep(delay)
        delay *= 2



