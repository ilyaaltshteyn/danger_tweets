import numpy as np, pandas as pd, random
string1 = 'hello this is a message for the aliens'
string2 = 'hello this is aint one for them'
string3 = 'aliens is alright though ya aint knowin this alright'

strings = [string1, string2, string3]

def onegram_finder(list_of_strings):
    """returns common strings of n words from input"""
    if len(list_of_strings) == 1:
        return 'list is only len 1!'
    parted_strings = []
    for string in list_of_strings:
        parted_strings.append(set(string.split(' ')))
    common = set.intersection(*[x for x in parted_strings])
    return common

def strings_selector(percent, list, num = 0):
    if percent != 0:
        num = int(np.round((float(percent)/100 * len(list)),0))
    rand_sample = random.sample(list,num)
    return rand_sample

dat = pd.read_csv('train_data.csv')
dat = dat.dropna(subset=['True danger tweet?'])
tweets = dat.Tweet

for x in range(1000):
    try: 
        out = onegram_finder(strings_selector(percent = 0,list =tweets, num = 4))
        if len(out) > 0:
            print out
        else:
            continue
    except:
        continue

# parted_strings = []
# for string in some_tweets:
#     parted_strings.append(set(string.split(' ')))



# print onegram_finder(strings)