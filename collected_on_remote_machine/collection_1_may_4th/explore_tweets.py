import pandas as pd
import matplotlib.pyplot as mpl

dir = '/Users/ilya/Projects/danger_tweets/collect tweets/collected_on_remote_machine/collection_1_may_4th/hydrated_tweets/'
file = 'hydrated1 2015-05-04 01:23:15.987682.txt'
filename = dir + file

openfile = open(filename, 'r')
import ast
hm = ast.literal_eval(openfile.readlines()[0][8:-1])
df = pd.DataFrame(hm)
df2 = df.T



df2.to_csv('test_hydrated_file.csv', encoding = 'utf-8')

dir = '/Users/ilya/Projects/danger_tweets/collect tweets/collected_on_remote_machine/collection_1_may_4th/dry_tweets/'
file = '2015-05-04 01:23:15.987682.txt'
filename = dir + file
openfile = open(filename, 'r')
import ast
lines = []
for line in openfile:
    lines.append(line)

hm = ast.literal_eval(openfile.readlines()[0][8:-1])
df = pd.DataFrame(hm)
df2 = df.T

df2.to_csv('test_UNhydrated_file.csv', encoding = 'utf-8')