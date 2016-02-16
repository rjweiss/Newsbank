import os, sys, re
from collections import defaultdict
from lxml import etree
from datetime import datetime
from pprint import pprint

'''Main method that tries to extract values for specific doc attributes via XPath'''
def parse_doc(xml_file):
	tree = etree.parse(xml_file)
	try:
		paper = tree.xpath('doc//sourceInfo/paper/text()')[0]
	except IndexError:
		paper = None
	try:
		show = tree.xpath('doc//sourceInfo/show/text()')[0]
	except IndexError:
		show = None
	try:
		datestring = tree.xpath('doc//sourceInfo/ymd/text()')[0]
		date = datetime.strptime(datestring, '%Y%m%d')
	except IndexError:
		date = None
	try:
		locations = tree.xpath('doc//locations/text()')[0]
	except IndexError:
		locations = None
	try:
		indexterms = tree.xpath('doc//indexterms/text()')[0]
		indexterms = [term.strip() for term in indexterms.split(';')]
	except IndexError:
		indexterms = None
	try:
		maintext = parse_maintext(tree.xpath('doc//maintext/text()')) 
	except lxml.etree.XPathSyntaxError:
		maintext = None

	return {
		'paper': paper, 
		'show': show,
		'date': date,
		'locations': locations,
		'indexterms': indexterms,
		'maintext': maintext 
 }	
	
'''This function will return a dictionary of names to a list of quotes from that person'''
#def get_quotes(maintext):
#	name_re = re.compile(r'([A-Z][A-Z]+(?=\s[A-Z])(?:\s[A-Z][A-Z]+)+)')
#	for line in maintext:

'''Main method that describes how to parse the main text of the file.  Returns a dictionary.'''
def parse_maintext(maintext):
	# XXX Fix cues, they are bad right now
	# XXX 
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
			continue
		text.append(line)

	result = {
		#'cues': dict(cues),
		'names': dict(names),
		'text': '|'.join(text) # Need to do a better job of grabbing the right text
	}
	return result

'''Helper function that applies parsing to all files that end with .xml'''
def handle_xml_file(ext, dirpath, names):
	for name in names:
		if name.endswith(ext):
			doc = parse_doc(os.path.join(dirpath, name))
			pprint(doc)
			sys.exit() # XXX End with processing a single document for now

'''Function that traverses data directory and finds all .xml files.'''
def process_files(rootdir):
	ext = '.xml'
	os.path.walk(rootdir, handle_xml_file, '.xml')

# XXX Refactor into a "run" or "start" method()
if __name__ == '__main__':
	DATADIR = '/data'
	process_files(DATADIR)



