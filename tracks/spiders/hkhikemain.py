from tracks.items import HKHikeItem
from pymongo import MongoClient
import scrapy
import time
import gpxpy 
import json

mongo_db = "trails"
mongo_collection = "HTHK"

class HTHKSpider(scrapy.Spider):
	name = 'HTHKmain'
	allowed_domains = ['hikingtrailhk.appspot.com']
	start_urls = ['https://hikingtrailhk.appspot.com/hk/search']

	def __init__(self, mongouri=None, *args, **kwargs):
		super(HTHKSpider, self).__init__(*args, **kwargs)
		client = MongoClient(mongouri)
		db = client[mongo_db]
		self.collection = db[mongo_collection]

	def parse(self, response):
		links = response.xpath(
            "//div[@class='rc_item']/div[@class='rc_link']/a/@href").getall()
		for link in links:
			id = link.split('/')[-1]
			if self.collection.find_one({"_id": id}) is None:
				yield scrapy.Request(link.replace("hikingtrailhk.appspot.com/hk/","hikingtrailhk.appspot.com/hk/gpx/"), callback=self.parseGPX)

	def parseGPX(self, response):
		item = HKHikeItem()
		gpx = gpxpy.parse(response.text)
		sel = scrapy.Selector(text=response.text)
		item = {
			'_id': response.request.url.split('/')[-1],
			'name': gpx.name,
			'desc': gpx.description,
			'length_2d': gpx.length_2d(),
			'raw': response.text
		}
		self.collection.insert_one(item)
		pass