import os, sys, re, ast, csv, json
from collections import defaultdict
from lxml import etree
from datetime import datetime
from pprint import pprint
from dateutil.parser import parse 

DOC_COUNTS = defaultdict(int)
SHOW_COUNTS = defaultdict(int)

'''Main method that tries to extract values for specific doc attributes via XPath'''
def parse_doc(xml_file):
	tree = etree.parse(xml_file)
	docs = tree.findall('doc')
	DOC_COUNTS[len(docs)] += 1
	for doc in docs:
		d = get_children(doc)
		d['sourceInfo'] = get_children(doc.find('sourceInfo'))
		d['maintext'] = parse_maintext(doc.xpath('maintext/text()'))
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
def parse_maintext(maintext):
	# XXX Fix cues, they are bad right now
	cue_re = re.compile(r'(\([A-Z][A-Z]+\))')
	#name_re = re.compile(r'([A-Z][A-Z]+(?=\s[A-Z])(?:\s[A-Z][A-Z]+)+)')
	name_re = re.compile(r'(\b[A-Z][A-Z.-]+\b)+')
	text = []
	names = defaultdict(int)
	cues = defaultdict(int)

	for line in maintext:
		cue = re.search(cue_re, line)
		name = re.findall(name_re, line)
		if name:
			names[' '.join(name)] +=1	
			if cue:
				cues[cue.group(0)] +=1
			#continue
		text.append(line)

	result = {
		#'cues': dict(cues),
		'names': dict(names),
		'text': '|'.join(text) # Need to do a better job of grabbing the right text
	}
	return result

def parse_date(string):
	try:
		parse(string)
		return True 
	except ValueError:
		return False
		
'''Helper function that increases the title count for files'''
def increment_show_counts(doc):
	try:
		SHOW_COUNTS[doc['sourceInfo']['paper']] += 1
	except KeyError:
		SHOW_COUNTS['null'] += 1
	
'''Helper function that applies parsing to all files that end with .xml'''
def handle_xml_file(ext, dirpath, names):
	for name in names:
		#print 'Current time = {t}'.format(t=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
		if name.endswith(ext):
			print 'Processing ' + name
			doc = parse_doc(os.path.join(dirpath, name))
			if not doc:
				return False 
			for d in doc:
				increment_show_counts(d)				
	return True			

'''Function that traverses data directory and finds all .xml files.'''
def process_files(rootdir):
	ext = '.xml'
	os.path.walk(rootdir, handle_xml_file, '.xml')

def write_results(outputdir):
	print 'Writing results to file'
	if SHOW_COUNTS:
		with open(os.path.join(outputdir, 'showcounts.json'), 'w') as f:
			json.dump(dict(SHOW_COUNTS), f)

	if DOC_COUNTS:
		DOC_COUNTS = {int(k): int(v) for k,v in DOC_COUNTS.items()}
		with open(os.path.join(outputdir, 'doccounts.json'), 'w') as f:
			json.dump(dict(DOC_COUNTS), f)
			
	print 'Total number of docs: {n}'.format(n=sum(DOC_COUNTS.itervalues()))

# XXX Refactor into a "run" or "start" method()
if __name__ == '__main__':
	DATADIR = '/data'
	RESULTDIR = '/work/results'
	process_files(DATADIR)
	write_results(RESULTDIR)


