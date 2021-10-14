import scrapy

class TracksItem(scrapy.Item):
	_id = scrapy.Field()

	length_2d = scrapy.Field()
	length_3d = scrapy.Field()
	ascent = scrapy.Field()
	descent = scrapy.Field()
	highest_ele = scrapy.Field()
	lowest_ele = scrapy.Field()
	uphill= scrapy.Field()
	downhill= scrapy.Field()

	moving_time = scrapy.Field()
	max_speed = scrapy.Field()

class HKHikeItem(scrapy.Item):
	_id = scrapy.Field()
	raw = scrapy.Field()
	name = scrapy.Field()
	desc = scrapy.Field()
	length_2d = scrapy.Field()