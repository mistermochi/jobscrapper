from tracks.items import HKHikeItem
from pymongo import MongoClient
import scrapy
import time
import gpxpy 
import json

mongo_db = "trails"
mongo_collection = "HTHK"

class HTHKSpider(scrapy.Spider):
	name = 'HTHK'
	allowed_domains = ['hikingtrailhk.appspot.com']
	start_urls = ['https://hikingtrailhk.appspot.com/hk/search?q=&r=new_territories&c=']

	def __init__(self, **kwargs):
		client = MongoClient(mongouri)
		db = client[mongo_db]
		self.collection = db[mongo_collection]
		super().__init__(**kwargs)

	def parse(self, response):
		links = response.xpath(
            "//div[@class='sr_type_link']/div[@class='sr_link']/a/@href").getall()
		for link in links:
			id = link.split('/')[-1]
			if collection.find_one({"_id": id}) is None:
				yield scrapy.Request(link.replace("hikingtrailhk.appspot.com/hk/","hikingtrailhk.appspot.com/hk/gpx/"), callback=self.parseGPX)
		nextPage = response.xpath("//div[@class='sr_paging']/div[@class='sr_p_link'][last()]/a/@href").get()
		yield scrapy.Request(nextPage, self.parse)


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
		collection.insert_one(item)
		pass