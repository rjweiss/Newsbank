import os, sys, json, re, csv
from collections import defaultdict, OrderedDict
from pprint import pprint

d = json.load(open('showcounts.json'))


markets = defaultdict(int)
channels = defaultdict(int)
master_by_dmca = defaultdict(int)
DMCAs = defaultdict(int)

DMCA_re = re.compile('([A-Z]{3,4})')
market_re = re.compile('\((.+)\)')
channel_re = re.compile('\[(.+)\]')

for k,v in d.items():
    market_found = re.search(market_re, k)
    channel_found = re.search(channel_re, k)
    if market_found:
        markets[market_found.group(1)] += v
    if channel_found:
        channels[channel_found.group(1)] += v  

for k,v in d.items():
#	print k
	DMCA_found = re.findall(DMCA_re, k)
	pprint(DMCA_found)
	if DMCA_found:
		#DMCAs[DMCA_found.group(0)] += v
		for item in DMCA_found:
			DMCAs[item] += v

code_map = dict()
network_map = dict()

with open('channel_names.csv') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        code_map[row['Code']] = row['Market']
        network_map[row['Code'].strip()] = row['Channel']      
      
codes_master = set(code_map.keys())
codes_newsbank = set(DMCAs.keys())
overlap = set(codes_master.intersection(codes_newsbank))
#pprint(codes_newsbank)

for k,v in d.items():
	DMCA_found = re.findall(DMCA_re, k)
	for item in DMCA_found:
		no_fly  = set(['ABC','CBS','CNN','CNNG','FOX','USA', 'NBC', 'NPR', 'PBS'])
		if item in codes_master:
			master_by_dmca[item] += v

pprint(dict(master_by_dmca))
print 'total docs = ' + str(sum(d.values()))
print 'total codes in master list = ' + str(len(codes_master))
print 'total codes found in newsbank = ' + str(len(codes_newsbank))
print 'total overlapping codes = ' + str(len(overlap))
print 'total master codes in newsbank = ' + str(sum(master_by_dmca.values()))
print 'missing values = ' + str(list(set(codes_master - overlap)))
