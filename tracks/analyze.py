import json
from pymongo import MongoClient
import gpxpy
from scrapy import Selector
from shapely import geometry
from shapely import wkt

mongo_uri = "mongodb://localhost:27017"
mongo_db = "tracks"
mongo_collection = "HTHK"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]
wpcollections = db["HTHKwaypoints"]


def combineAll():
	results = geometry.Point()
	all = collection.find({'bounds': { '$exists': True }}, {'bounds': 1})
	for one in all:
		bounds = wkt.loads(one['bounds'])
		results = results.union(bounds)
	print(results.area);

combineAll()