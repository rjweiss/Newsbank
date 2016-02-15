import os, sys, re
import xml.etree.ElementTree
from collections import defaultdict
from lxml import etree
from datetime import datetime
from pprint import pprint

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
	maintext = parse_maintext(tree.xpath('doc//maintext/text()')) 
# XXX This should be its own function that parses out quotes and the like separately

	return {
		'paper': paper, 
		'show': show,
		'date': date,
		'locations': locations,
		'indexterms': indexterms,
		'maintext': maintext 
 }	
	
def parse_maintext(maintext):
	# XXX Fix cues, they are bad right now
	cue_re = re.compile(r'(\([A-Z][A-Z]+\))')
	name_re = re.compile(r'([A-Z][A-Z]+(?=\s[A-Z])(?:\s[A-Z][A-Z]+)+)')
	text = []
	names = defaultdict(int)
	cues = defaultdict(int)

	for line in maintext:
		cue = re.search(cue_re, line)
		name = re.search(name_re, line)
		if name:
			names[name.group(0)] +=1	
			if cue:
				cues[cue.group(0)] +=1
			continue
		text.append(line)

	result = {
		#'cues': dict(cues),
		'names': dict(names),
		'text': '|'.join(text) 
	}
	return result

# XXX Refactor into a "run" or "start" method()
if __name__ == '__main__':
	for d1 in os.listdir('/data'):
		curr_d = os.path.join('/data/' + d1)
		dirs = os.listdir(curr_d)
		for d2 in dirs:
			curr_d2 = os.path.join(curr_d, d2)
			dirs2 = os.listdir(curr_d2)
			for f in dirs2:
				fullpath = os.path.join(curr_d2, f)
				with open(fullpath, 'r') as xml_file:
					xml_file = os.path.join(curr_d2, fullpath)
					try:
						doc = parse_doc(xml_file)
					except Error as e:
						print e
				sys.exit() # Just to get through for testing purposes
