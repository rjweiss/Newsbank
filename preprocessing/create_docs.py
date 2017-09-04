import logging, os, sys, sqlite3
from datetime import datetime
from gensim import corpora, utils
from gensim.models import wrappers, LdaMulticore
from collections import namedtuple
from parse import parse_doc
from pprint import pprint
from datetime import date
from dateutil.rrule import rrule, DAILY

#Row = namedtuple('Row', 'date dma path station show')
TEMPORAL = 'day'
UNIT = 'market'
MODELPATH = '{time}{unit}/'.format(time=TEMPORAL, unit=UNIT)
DOCSPATH = '{time}{unit}_docs/'.format(time=TEMPORAL, unit=UNIT)
FORMAT = "[%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)s() ]: %(message)s"

def setup_logging(fname):
	logging.basicConfig(
	     filename=fname,
	     level=logging.DEBUG,
	     format=FORMAT,
	     datefmt='%H:%M:%S'
	 )
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-s %(levelname)-s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)
	logger = logging.getLogger(__name__)
	return logger

def setup_db(dbname):
	logger.info('Connecting to database')
	conn = sqlite3.connect(dbname)
	return conn.cursor()

def get_markets(cursor):
	query = '''
		select distinct market from meta
	'''	
	return [str(m[0]) for m in cursor.execute(query)]

def get_stations(cursor):
	query = '''
		select distinct code from meta
	'''
	return [str(m[0]) for m in cursor.execute(query)]

def get_paths(code, **kwargs):
	level = None
	if kwargs['unit'] == 'day':
		level = '%Y%m%d'
	elif kwargs['unit'] == 'month':
		level = '%Y%m'
	elif kwargs['unit'] == 'year':
		level = '%Y'

	if kwargs['market']:
		query = '''
			select strftime('{unit}', aired) as date, meta.market as dma, meta.code as code, path, station, show from files
	  	inner join meta on files.station = meta.code
	  	where date = '{date}' and dma = '{market}'
	  	'''.format(
				market=code,
				unit=level,
				date=kwargs['date'])
	if kwargs['station']:
		query = '''
			select strftime('{unit}', aired) as date, meta.market as dma, meta.code as code, path, station, show from files
	  	inner join meta on files.station = meta.code
	  	where date = '{date}' and code = '{code}'
	  	'''.format(
				code=code,
				unit=level,
				date=kwargs['date'])

	cursor.execute(query)
	logger.info('Query executed.')
	paths = []
	for el in cursor:
		#row = Row(*el)
#		paths.append(row.path)
		paths.append(el[3])

	return paths

def create_docs(*args, **kwargs):
	sw_file = open('stopwords.txt', 'r')
	stopwords = sw_file.readline().split(',')
	stopwords = set([w.strip('/n').strip().lower() for w in stopwords])
	if kwargs['market']:
		iterable = get_markets(cursor)
	if kwargs['station']:
		iterable = get_stations(cursor)

	for code in iterable:
		paths = get_paths(code, **kwargs)
		words = []
		for fname in paths:
			if not os.path.isfile(fname):
				continue
			print 'Parsing ' + str(fname)
			docs = parse_doc(fname)
			for doc in docs:
				tokens = utils.simple_preprocess(doc['maintext']['text'])
				tokens = [token for token in tokens if token not in stopwords]
				words.extend(tokens)
		print "Writing to file."
		words = [word.encode('utf8') for word in words]
		outfname = '_'.join([code.strip(), kwargs['date'], kwargs['unit']]) + '.txt'
		outpath = os.path.join(DOCSPATH + outfname)
		with open(outpath, 'w') as outfile:
			outfile.write(' '.join(words))
		
def iter_docs(docs_dir):
	for fname in os.listdir(docs_dir):
		doc = open(os.path.join(docs_dir, fname)).read()
		if len(doc) == 0:
			logger.info('Skipping {}'.format(fname))
			continue
		# XXX filter stopwords here
		yield utils.simple_preprocess(doc)

def day_gen():
	a = date(2007,1,1)
	b = date(2007,12,31)
	
	for dt in rrule(DAILY, dtstart=a, until=b):
		yield dt.strftime('%Y%m%d')


class NewsbankCorpus(corpora.TextCorpus):
	def __init__(self, path):
		self.docs_dir=DOCSPATH
		dict_fname = '{path}corpus.dict'.format(path=MODELPATH)
		corp_fname = '{path}corpus.txt'.format(path=MODELPATH)

		#if os.path.isfile(corp_fname):
		#	logger.info('Loading dictionary from corpus file')
		#	self.dictionary = corpora.Dictionary.from_documents(corp_fname)
		if os.path.isfile(dict_fname):
			logger.info('Loading dictionary from dictionary file')
			self.dictionary = corpora.Dictionary.load(dict_fname)
		else:
			logger.info('No corpus or dictionary found; creating new dictionary')
			self.dictionary = corpora.Dictionary(iter_docs(path))
			self.dictionary.save(dict_fname)
		self.dictionary.filter_extremes(no_below=0, keep_n=30000)

	def __iter__(self):
		for tokens in iter_docs(self.docs_dir):
			yield self.dictionary.doc2bow(tokens)
	
if __name__ == '__main__':
	logger = setup_logging(MODELPATH +'output.log')
	logging.basicConfig(level=logging.WARNING)
	cursor = setup_db('/home/ssh_rjweiss/newsbank.db')
	logger.info('Creating docs')
	#create_docs(cursor, unit='month', date='200702', market=True, station=False)
	dg = day_gen()
	for d in dg:
		create_docs(cursor, unit='day', date=d, market=True, station=False)
		logger.info('Day {d} finished'.format(d=d))
	
	
