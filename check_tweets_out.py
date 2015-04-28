file = '/Users/ilya/Projects/twitter_danger/out.txt'
tweets_list = []
with open(file, 'r') as tweets:
    for line in tweets:
        tweets_list.append(line)

