#!/usr/bin/env python

import json
import sys

import pymongo

def iter_row(fn):
	raw_data = json.load(open(fn))
	cols = raw_data['meta']['view']['columns']
	data = raw_data['data']
	for i, x in enumerate(data):
		dd = {}
		for j, y in enumerate(x):
			dd[cols[j]['name'].lower()] = y
		try:
			dd['geo'] = {
				'type': 'Point',
				'coordinates': [float(dd['location'][2]), float(dd['location'][1])]
			}
		except:
			pass
		yield dd

if __name__ == "__main__":
	client = pymongo.MongoClient()
	db = client['medrank']
	collection = db[sys.argv[1]]
	i = 0
	for x in iter_row(sys.argv[2]):
		if x.get('geo') or sys.argv[1] != 'hospital': 
			collection.insert(x)
			i += 1
	print i
