from pathlib import Path

import scrapy


class ScrapeExample(scrapy.Spider):
    name = "quotes"

    custom_settings = {
        "ITEM_PIPELINES": {
            "espn.NBA.pipelines.pipelines.EspnPipeline": 300
        }
    }

    async def start(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
