import scrapy

class PlayerStats(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
