import json
from pymongo import MongoClient
import gpxpy
from scrapy import Selector
from shapely import geometry
from shapely import wkt

mongo_uri = "mongodb+srv://mrmochi:mochitabetai@hike.t9anp.mongodb.net/"
mongo_db = "trails"
mongo_collection = "HTHK"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]
wpcollections = db["HTHKwaypoints"]


def findSimilar(id):
	def getoverlap(e):
		return e['overlap']
	results = [];
	tester = collection.find_one({'_id': id}, {'bounds': 1})
	tester_bounds = wkt.loads(tester['bounds'])
	all = collection.find({'bounds': { '$exists': True }}, {'bounds': 1})
	for one in all:
		bounds = wkt.loads(one['bounds'])
		overlap = bounds.intersection(tester_bounds).area**2 / tester_bounds.area / bounds.area
		if overlap > 0.1:
			results.append({"id": one['_id'], "overlap": overlap})
	results.sort(reverse=True, key=getoverlap)
	print(results);

def updateBoundShape():
	all = collection.find({'bounds': None })
	for one in all:
		gpx = gpxpy.parse(one['raw'])
		print("{0} checking".format(one['_id']))
		tracks = []
		for track in gpx.tracks:
			segments = []
			for segment in track.segments:
				if len(segment.points) < 2:
					continue # ignore single points
				points = []
				for point in segment.points:
					points.append((point.latitude, point.longitude))
				segments.append(points)
			tracks.append(segments)
		# flatlist
		obj = [item for sublist in tracks for item in sublist]
		if len(obj) == 0:
			print("{0} track has no point".format(one['_id']))
			continue
		# get shape of path
		shape = geometry.MultiLineString(obj).buffer(0.0002,1)
		out = wkt.dumps(shape, trim=True)

		# to mongodb
		try:
			result = collection.find_one_and_update({"_id" : one['_id']}, {'$set': { 'bounds': out }})
			print("{0} updated".format(one['_id']))
		except:
			print ("{0} cannot be parsed".format(one['_id']))


def updateLinks():
	all = collection.find({"links": None })
	for one in all:
		links = Selector(text=one['raw']).xpath('//gpx/metadata/link/@href').getall()
		if len(links) > 0:
			try:
				result = collection.find_one_and_update(
			   	 {"_id" : one['_id']}, {"$set": { "links": links }}
				)
				print("{0} updated with {1} links".format(one['_id'], len(links)))
			except:
    				print ("{0} cannot be parsed".format(one['_id']))

def extractwaypoints():
	all = collection.find()
	for one in all:
		for point in gpxpy.parse(one['raw']).waypoints:
			try:
				wpcollections.insert_one( {
					"properties": {
						"name": point.name,
						"symbol": point.symbol,
						"source": one['_id']
					},
					"geometry": { "type": "Point", "coordinates": [ point.longitude, point.latitude ] }
				});
			except:
    				print ("{0} failed to collect waypoints".format(one['_id']))

def updateTags():
	all = collection.find()
	for one in all:
		tag = []
		try:
			for extension in gpxpy.parse(one['raw']).metadata_extensions:
				if extension.tag == "{https://hikingtrailhk.appspot.com/xml/gpxextensions/v1}categoryid":
					tag.append(extension.text)
			if len(tag) > 0:
				print(len(tag))
		except:
    			print ("{0} cannot be parsed".format(one['_id']))


def updateTags():
	all = collection.find()
	for one in all:
		tag = []
		try:
			for extension in gpxpy.parse(one['raw']).metadata_extensions:
				if extension.tag == "{https://hikingtrailhk.appspot.com/xml/gpxextensions/v1}categoryid":
					tag.append(extension.text)
			if len(tag) > 0:
				print(len(tag))
		except:
    			print ("{0} cannot be parsed".format(one['_id']))

def updateBounds():
	all = collection.find()
	for one in all:
		bounds = gpxpy.parse(one['raw']).get_bounds()
		try:
			result = collection.find_one_and_update(
			    {"_id" : one['_id']},
			    {"$set":
 			       {
					"min_latitude": bounds.min_latitude,
					"max_latitude": bounds.max_latitude,
					"min_longitude": bounds.min_longitude,
					"max_longitude": bounds.max_longitude,
				}
 			   }
			)

		except:
    			print ("{0} cannot be parsed".format(one['_id']))

updateBoundShape()