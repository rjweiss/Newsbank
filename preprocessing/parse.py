import os, sys, re, ast, csv, json, re, codecs
from collections import defaultdict
from lxml import etree
from datetime import datetime
from pprint import pprint
from dateutil.parser import parse 

DOC_COUNTS = defaultdict(int)
SHOW_COUNTS = defaultdict(int)

'''Reconstructs an individual doc from xml to dict'''
def parse_doc(xml_file):
	tree = etree.parse(xml_file)
	docs = tree.findall('doc')
	DOC_COUNTS[len(docs)] += 1

	for index, doc in enumerate(docs):
		d = get_children(doc)
		# Files with "delete" status don't have data.  Ignore them.
		if d['STATUS'] == 'delete':
			continue

		# Set document values
		d['index'] = index
		d['sourceInfo'] = get_children(doc.xpath('sourceInfo')[0])
		d['maintext'] = parse_maintext(doc.xpath('maintext/text()'))
		
		# Shows don't always have their title in the right location
		try:
			d['show'] = d['sourceInfo']['show']
		except KeyError:
			try:
				d['show'] = d['sourceInfo']['paper']
			except KeyError:
				d['show'] = None
		d['network'] = get_network(d['sourceInfo']['paper'])
		d['dma'] = get_dma(d['sourceInfo']['paper'])
		#except KeyError:
		#	d['show'] = None
		#	d['network'] = None
		#	d['dma'] = None
		yield d

'''Helper function to grab a dictionary of the next level's children'''	
def get_children(node):
	children = node.getchildren()
	results = defaultdict(str)
	for child in children:
		results[child.tag] = child.text
	return dict(results)

'''This function will return a dictionary of names to a list of quotes from that person'''
#def get_quotes(maintext):
#	name_re = re.compile(r'([A-Z][A-Z]+(?=\s[A-Z])(?:\s[A-Z][A-Z]+)+)')
#	for line in maintext:

'''Main method that describes how to parse the main text of the file.  Returns a dictionary.'''
# XXX Main text parsing needs a lot of work
# XXX Idea: prepare a key-value of names to text
def parse_maintext(maintext):
	# XXX Fix cues, they are bad right now
	#cue_re = re.compile(r'(\([A-Z][A-Z]+\))')
	name_re = re.compile(r'(\b[A-Z][A-Z.-]+\b)+')
	text = []
	names = defaultdict(int)
	#cues = defaultdict(int)

	skip = False
	for line in maintext:
		if skip:
			if 'END VIDEO CLIP' in line:
				skip = False
				continue
		if 'BEGIN VIDEO CLIP' in line:
			skip = True
			continue
		#cue = re.search(cue_re, line)
		name = re.findall(name_re, line)
		if name:
			names[' '.join(name)] +=1	
			continue
			#if cue:
			#continue
			#	cues[cue.group(0)] +=1
			
		text.append(line)

	result = {
		#'cues': dict(cues),
		'names': dict(names),
		'text': ''.join(text) #XXX Need to do a better job of grabbing the right text
	}
	return result

'''Helper function to check if there is a date in the string'''
def parse_date(string):
	try:
		parse(string, fuzzy=True)
		return True 
	except ValueError:
		return False
		
def get_network(string):
	network_re = re.compile('\[(.+)\]')
	network_found = re.search(network_re, string)
	if network_found:
		return network_found.group(1)
	else:
		return None 

def get_dma(string):
	dma_re = re.compile('\s([A-Z][A-Z][A-Z][A-Z]?)\s')
	dma_found = re.search(dma_re, string)
	if dma_found:
		return dma_found.group(1)
	else:
		return None 

'''Helper function that increases the title count for files'''
def increment_show_counts(doc):
	if doc['sourceInfo']['paper']:
		SHOW_COUNTS[doc['sourceInfo']['paper']] += 1
	else:
		SHOW_COUNTS['null'] += 1
	
'''Helper function that applies parsing to all files that end with .xml'''
def handle_xml_file(ext, dirpath, names):
	for name in names:
		if name.endswith(ext):
			print 'Processing ' + name # XXX Move to proper logging
			docs = parse_doc(os.path.join(dirpath, name))
			if not docs:
				return False 
			for d in docs:
				pprint(d)
				sys.exit()
				increment_show_counts(d)				
	return True			

'''Function that traverses data directory and finds all .xml files.'''
def process_files(rootdir):
	ext = '.xml'
	os.path.walk(rootdir, handle_xml_file, '.xml')

def write_results(outputdir):
	print 'Writing results to file' # XXX Move to proper logging
	if SHOW_COUNTS:
		with open(os.path.join(outputdir, 'showcounts.json'), 'w') as f:
			json.dump(dict(SHOW_COUNTS), f)

	#if DOC_COUNTS:
	#	DOC_COUNTS = {int(k): int(v) for k,v in DOC_COUNTS.items()}
	#	with open(os.path.join(outputdir, 'doccounts.json'), 'w') as f:
	#		json.dump(dict(DOC_COUNTS), f)
			
	print 'Total number of docs: {n}'.format(n=sum(DOC_COUNTS.itervalues()))

# XXX Refactor into a "run" or "start" method()
if __name__ == '__main__':
	DOC_COUNTS = defaultdict(int)
	SHOW_COUNTS = defaultdict(int)
	DATADIR = '/data'
	RESULTDIR = '/work/results'
	process_files(DATADIR)
	write_results(RESULTDIR)
