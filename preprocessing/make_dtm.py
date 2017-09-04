from parse import parse_doc
from sklearn.feature_extraction.text import CountVectorizer # XXX Do we want TF-IDF transfomration?
from sklearn.preprocessing import Normalizer
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from numpy import savetxt
import sqlite3
import sys
import string
from pprint import pprint

conn = sqlite3.connect('/home/ssh_rjweiss/newsbank.db')
cursor = conn.cursor()

cursor.execute('''select strftime('%Y-%m-%d', aired) as date, meta.market as dma, path, station, show from files 
	inner join meta on files.station = meta.code 
	where date = '2007-01-01' 
	order by dma''')

def clean_text(text, stemmer):
	lower = text.lower()
	no_punct = [x.strip(string.punctuation) for x in lower] 
	no_digits = ''.join([x.strip(string.digits) for x in no_punct])
	tokens = word_tokenize(no_digits)
	#filtered = [w for w in tokens if not w in stopwords.words('english')]
	stemmed = [stemmer.stem(w) for w in tokens]
	return ' '.join(stemmed)

vectorizer = CountVectorizer(stop_words='english', max_features=1000)#n_features=10, stop_words='english', non_negative=True, norm=None, binary=False, strip_accents='unicode', analyzer='word')

corpus = []
doc_meta = []
stemmer = PorterStemmer()
for row in cursor:
	print 'Parsing {}'.format(row[2])	
	date = row[2].split('/')[-1].split('.')[0]
	docs = parse_doc(row[2]) # XXX Need to improve parse_doc to clear out video clips
	for idx, el in enumerate(docs):
		doc_meta.append("{date},{dma},{station},{show},{idx}".format(date=date, dma=row[1].strip(), station=row[3], show=row[4], idx=idx))
		text = clean_text(el['maintext']['text'], stemmer)
		corpus.append(text)

dtm =	vectorizer.fit_transform(corpus)
with open('test_meta.csv', 'w') as outfile:
	for item in doc_meta:
		outfile.write("{}\n".format(item))
	
vocab = vectorizer.get_feature_names()
savetxt('test_dtm.csv', dtm.toarray(), delimiter=',', fmt='%d', header=','.join(vocab))
pprint(dtm.get_shape())
#print dtm.get_feature_names()
#tdm.write_csv('test.csv', cutoff=1)
