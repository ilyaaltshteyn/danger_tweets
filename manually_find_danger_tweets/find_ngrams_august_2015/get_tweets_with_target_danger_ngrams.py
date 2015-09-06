from pymongo import MongoClient
client = MongoClient()
db = client.tweets
collect = db.random_sample_remote_computer

left_out = ['ebola', 'MERS', '\"avian flu\"', 'cholera',
'dengue', 'malaria', 'anthrax', 'bacteria', 'drought', 'snake']

target_ngrams = ['Salmonella', '\"food poisoning\"', '\"e. coli\"', '\"e coli\"',
'outbreak', '\"contaminated water\"', 'contamination',
'\"air quality index\"', '\"dangerous drugs\"', '\"synthetic drugs\"', '\"health warning\"',
'\"oil spill\"', '\"water shortage\"', '\"fracking earthquakes\"', '\"water quality\"', 
'\"severe weather\"', '\"Tornado warning\"', '\"Flood warning\"', 'windstorm', '\"extreme heat\"', 
'\"hurricane warning\"', '\"hurricane threat\"', '\"tsunami warning\"', '\"tsunami threat\"', 
'\"mountain lion\"', '\"rabid dog\"', '\"dog attack\"', '\"dog bite\"', 'alligator',
'\"speed trap\"', '\"triggering tax audit\"', '\"stock market crash\"', '\"terrorism alert\"', 
'\"bomb threat\"', '\"plane hijacking\"', '\"Is a scam\"', '\"Scam warning\"', '\"Scam alert\"', 
'\"new scam\"', '\"new e-scam\"', '\"don’t fall for\"', '\"scams spreading\"', '\"identity theft\"', 
'\"dangerous neighborhood\"', '\"child molester\"', '\"sex offender\"', '\"amber alert\"', '\"prison break\"', 
'\"drug dealer\"', 'kidnapping', '\"There is a gunman\"', '\"Suspicious person\"', '\"Dangerous person\"', 
'\"dangerous man\"', '\"dangerous men\"', '\"dangerous woman\"', '\"dangerous women\"', 
'\"electric lines down\"', '\"rip tide\"', 'sharks', '\"beach advisory\"', '\"Dangerous driving conditions\"', 
'\"Unsafe driving conditions\"', '\"Dangerous road conditions\"', '\"Unsafe road conditions\"']

# prepend "causes" and "cause" to the following:
extras = ['alzheimers', 'arthritis', 'asthma', 'autism', 'back pain', 'bladder cancer', 
'bone cancer', 'brain cancer', 'breast cancer', 'brain tumor', 'bronchitis', 
'acute bronchitis', 'cancer', 'carpal tunnel', 'celiac disease', 'cervical cancer', 
'crohns disease', 'depression', 'diabetes', 'down syndrome', 'dyslexia', 'epilepsy', 
'erectile disfunction', 'fybromyalgia', 'flu', 'gallstone', 'herpes', 'gout', 
'cardiovascular disease', 'hepatitis', 'hyperthyrodism', 'hypertension', 
'high blood pressure', 'kidney stone', 'leukemia', 'liver tumor', 'miscarriage', 
'multiple sclerosis', 'obesity', 'obsessive compulsive disorder', 'osteoporosis',
'parkinsons', 'pneumonia', 'preterm birth', 'psoriasis', 'rosacea', 'schizophrenia', 
'sinusitis', 'skin cancer', 'smallpox', 'ulcers', 'jaundice', 'childsafetyweek',
'child safety']

target_ngrams.extend(['\"causes' + x + '\"' for x in extras])
target_ngrams.extend(['\"cause' + x + '\"' for x in extras])
target_ngrams = [x.strip().lower() for x in target_ngrams]

def strip_non_ascii(text):
        """Replaces all non-ascii characters in the tweet with a space. Returns
        tweet."""
        return ''.join([i if ord(i) < 128 else ' ' for i in text])

with open('target_danger_ngram_tweets.txt', 'w') as outfile:
    outfile.write('Tweet\n')

total = 0
for target_ngram in target_ngrams:
    found = collect.find({ '$text' : {'$search': target_ngram} })
    for doc in found:
        with open('target_danger_ngram_tweets.txt', 'a') as outfile:
            t = strip_non_ascii(doc['text'])
            total += 1
            if total % 100 == 0: print total
            outfile.write(t + '\n')

