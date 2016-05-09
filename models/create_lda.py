import logging, os, sys, sqlite3
from datetime import datetime
from gensim import corpora, utils
from gensim.models import wrappers
from collections import namedtuple
from parse import parse_doc
from pprint import pprint

Row = namedtuple('Row', 'date dma path station show')
MODELPATH = 'temp_year/'
FORMAT = "[%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

def setup_logging(fname):
	logging.basicConfig(
	     filename=fname,
	     level=logging.DEBUG,
	     format=FORMAT,
	     datefmt='%H:%M:%S'
	 )
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-4s %(levelname)-4s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)
	logger = logging.getLogger(__name__)
	return logger

def setup_db(dbname):
	logger.info('Connecting to database')
	conn = sqlite3.connect(dbname)
	return conn.cursor()

#def build_query():

def get_paths(unit, date, cursor):
	#logger.info('Connecting to db')
	#conn = sqlite3.connect('/home/ssh_rjweiss/newsbank.db')
	#cursor = conn.cursor()

	cursor.execute('''select strftime('{unit}', aired) as date, meta.market as dma, path, station, show from files
	  inner join meta on files.station = meta.code
	  where date = '{date}'
	  order by dma'''.format(
			unit=unit,
			date=date))
	logger.info('Query executed.')
	paths = []
	for el in cursor:
		row = Row(*el)
		paths.append(row.path)

	return paths
		
def text_generator(paths):
	for fname in paths:
		result = parse_doc(fname)
		for doc in result:
			logger.debug('Processing ' + str(fname))
			yield utils.simple_preprocess(doc['maintext']['text'])

class NewsbankCorpus(object):
	def __init__(self, paths):
		self.paths = paths
		dict_fname = '{path}/corpus.dict'.format(path=MODELPATH)
		corp_fname = '{path}/corpus.txt'.format(path=MODELPATH)

		if os.path.isfile(dict_fname):
			logger.info('Loading dictionary from dict file')
			self.dictionary = corpora.Dictionary.load(dict_fname)
		#elif os.path.isfile(corp_fname):
		#	logger.info('Loading dictionary from corpus file')
		#	self.dictionary = corpora.Dictionary.from_corpus(corp_fname)
		else:
			logger.info('No corpus or dictionary found; creating new dictionary')
			self.dictionary = corpora.Dictionary(text_generator(paths))
			self.dictionary.save(dict_fname)

		self.dictionary.filter_extremes()

	def __iter__(self):
		for tokens in text_generator(self.paths):
			yield self.dictionary.doc2bow(tokens)
	
if __name__ == '__main__':
	logger = setup_logging('temp_year.log')
	cursor = setup_db('/home/ssh_rjweiss/newsbank.db')
	paths = get_paths(unit='%Y', date='2007', cursor=cursor)
	logger.info('Creating corpus from {count} files'.format(count=len(paths)))
	corpus = NewsbankCorpus(paths)
	mallet_path = '/work/Mallet/bin/mallet'
	logger.info('Now fitting model')
	model = wrappers.LdaMallet(mallet_path, corpus, num_topics=20, id2word=corpus.dictionary, prefix=MODELPATH, workers=400)
	model.save('test.model')


