import scrapy

class Player(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    stats = scrapy.Field()

