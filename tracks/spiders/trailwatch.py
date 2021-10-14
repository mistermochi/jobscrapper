from tracks.items import TracksItem
import scrapy
import time
import gpxpy 
import json

class TrailwatchSpider(scrapy.Spider):
	name = 'trailwatch'
	allowed_domains = ['trailwatch.hk']
	start_urls = ['https://www.trailwatch.hk/']

	def parse(self, response):
		form_data = {'start': '600', 'pageSize': '100', 'sort': 'update'}
		yield scrapy.FormRequest(
			'https://www.trailwatch.hk/?t=getActivities',
			formdata=form_data,
                        callback=self.parseFeed)

	def parseFeed(self, response):
		feed = json.loads(response.text)
		for item in feed:
			if item['status'] == "Finished":
				yield scrapy.Request("https://www.trailwatch.hk/?t=gpx&i={0}&type=Activity".format(item['activityId']), 
					callback=self.parseActivity)

	def parseActivity(self, response):
		item = TracksItem()
		gpx = gpxpy.parse(response.text)
		
		for track in gpx.tracks:
			try:
				item['_id'] = response.xpath('//gpx/trk/id/text()').get()

				item['length_2d'] = gpx.length_2d()
				item['length_3d'] = gpx.length_3d()
				item['ascent'] = response.xpath('//gpx/trk/ascent/text()').get()
				item['descent'] = response.xpath('//gpx/trk/descent/text()').get()
				item['highest_ele'] = response.xpath('//gpx/trk/highestele/text()').get()
				item['lowest_ele'] = response.xpath('//gpx/trk/lowestele/text()').get()

				uphill, downhill = gpx.get_uphill_downhill()
				item['uphill'] = uphill
				item['downhill'] = downhill

				moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx.get_moving_data()
				item['moving_time'] = moving_time
				item['max_speed'] = max_speed

				yield item

			except IndexError:
				pass