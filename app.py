#!/usr/bin/env python

from flask import abort, Flask, render_template, Response, request
from flask.ext.pymongo import PyMongo

from bson.json_util import dumps


app = Flask(__name__)
app.config['DEFAULT_SEARCH_RADIUS'] = 25  # in miles
app.config['MAX_SEARCH_RADIUS'] = 100  # in miles
app.config['MONGO_DBNAME'] = 'medrank'
mongo = PyMongo(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/nearby')
def nearby():
	try:
		radius = min(int(request.args.get('radius', app.config['DEFAULT_SEARCH_RADIUS'])), app.config['MAX_SEARCH_RADIUS'])
		lng = float(request.args.get('lng'))
		lat = float(request.args.get('lat'))
	except TypeError, ValueError:
		abort(400)
	query = {"geo": {"$within": {"$centerSphere": [[lng, lat], radius / 3963.2]}}}
	results = list(mongo.db.hospital_rank.find(query))
	return Response(dumps(results), mimetype='application/json')
	

@app.route('/about')
def about():
	return render_template('about_us.html')

@app.route('/map')
def medrank_map():
	return render_template('map.html')

@app.route('/references')
def references():
	return render_template('references.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9080, debug=True)
