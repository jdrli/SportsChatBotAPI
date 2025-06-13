import scrapy


class EspnspiderSpider(scrapy.Spider):
    name = "espnSpider"
    allowed_domains = ["espn.com"]
    start_urls = ["https://espn.com"]

    def parse(self, response):
        pass
