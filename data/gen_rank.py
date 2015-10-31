#!/usr/bin/env python

import json
import math

import pymongo


client = pymongo.MongoClient()

# define stats

_MONGO_STATS = """
[
	{ "_id" : "OP_22", "min" : 0, "max" : 22, "avg" : 1.7037411526794741 },
	{ "_id" : "MORT_30_HF", "min" : 7.2, "max" : 18.5, "avg" : 11.695064935064966 },
	{ "_id" : "MORT_30_PN", "min" : 6.9, "max" : 20.3, "avg" : 11.61268382352938 },
	{ "_id" : "MORT_30_COPD", "min" : 4.8, "max" : 13.8, "avg" : 7.770741964553919 },
	{ "_id" : "MORT_30_CABG", "min" : 1.6, "max" : 9.2, "avg" : 3.2702839756592224 },
	{ "_id" : "READM_30_HOSP_WIDE", "min" : 11.4, "max" : 19.8, "avg" : 15.22763354967551 },
	{ "_id" : "H_STAR_RATING", "min" : 1, "max" : 5, "avg" : 3.196876913655848 },
	{ "_id" : "MORT_30_AMI", "min" : 9.9, "max" : 19.5, "avg" : 14.155809935205163 },
	{ "_id" : "PSI_90_SAFETY", "min" : 0.37, "max" : 1.99, "avg" : 0.7956737825216814 },
	{ "_id" : "MORT_30_STK", "min" : 8.7, "max" : 22.3, "avg" : 14.865343811394899 },
	{ "_id" : "MSPB_1", "min" : 0.49, "max" : 1.63, "avg" : 0.983377371273716 },
	{ "_id" : "MORT_30_MEAN", "min" : 1.6, "max" : 22.3, "avg" : 11.213570038910573 }
]
"""

_temp = json.loads(_MONGO_STATS)
MONGO_STATS = {}
for x in _temp:
	MONGO_STATS[x['_id']] = x
	x.pop('_id')


pids = client.medrank.hospital.distinct('provider id')
client.medrank.hospital_rank.drop()
i = 0
scores = []
for pid in pids:
	pd = {}
	for x in client.medrank.hospital.find({'provider id': pid}):
		for y in ('hospital name', 'location', 'geo', 'phone number'):
			if not pd.get(y):
				pd[y] = x.get(y)
		if math.isnan(x['score']):
			pd[x['measure id']] = MONGO_STATS[x['measure id']]['avg']
		else:
			pd[x['measure id']] = x['score']
	for x in MONGO_STATS.keys():  # fill with averages if not present
		if x not in pd:
			pd[x] = MONGO_STATS[x]['avg']
	pd['MORT_30_MEAN'] = (pd['MORT_30_HF'] + pd['MORT_30_PN'] + pd['MORT_30_COPD'] + pd['MORT_30_CABG'] + pd['MORT_30_AMI'] + pd['MORT_30_STK']) / 6.0
	survival = (pd['MORT_30_MEAN'] - MONGO_STATS['MORT_30_MEAN']['min']) * 10000 / (100 * (MONGO_STATS['MORT_30_MEAN']['max'] - MONGO_STATS['MORT_30_MEAN']['min']))
	non_readmit = (MONGO_STATS['READM_30_HOSP_WIDE']['max'] - pd['READM_30_HOSP_WIDE']) * 10000 / (100 * (MONGO_STATS['READM_30_HOSP_WIDE']['max'] - MONGO_STATS['READM_30_HOSP_WIDE']['min']))
	pt_satisfaction = pd['H_STAR_RATING'] * 20
	spp = (pd['MSPB_1'] - MONGO_STATS['MSPB_1']['min']) * 10000 / (100 * (MONGO_STATS['MSPB_1']['max'] - MONGO_STATS['MSPB_1']['min']))
	percent_seen = (pd['OP_22'] - MONGO_STATS['OP_22']['min']) * 10000 / (100 * (MONGO_STATS['OP_22']['max'] - MONGO_STATS['OP_22']['min']))
	complications = (pd['PSI_90_SAFETY'] - MONGO_STATS['PSI_90_SAFETY']['min']) * 10000 / (100 * (MONGO_STATS['PSI_90_SAFETY']['max'] - MONGO_STATS['PSI_90_SAFETY']['min']))
	score = 0.25 * survival + 0.25 * non_readmit + 0.15 * spp + 0.15 * complications + 0.1 * percent_seen + 0.1 * pt_satisfaction 
	score = 2 * score
	pd['score'] = score
	scores.append(score)
	client.medrank.hospital_rank.insert(pd)
	i += 1

scores.sort(reverse=True)
for x in client.medrank.hospital_rank.find():
	x['rank'] = scores.index(x['score']) + 1
	client.medrank.hospital_rank.replace_one({'_id': x['_id']}, x)
print i	
