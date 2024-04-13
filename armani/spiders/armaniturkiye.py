from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from ..items import ArmaniItem


class ArmaniTurkiyeSpider(CrawlSpider):
    name = "armaniturkiye"

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'armani.middlewares.ArmaniTurkiyeDownloaderMiddleware': 443,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    allowed_domains = ["armaniturkiye.com"]
    start_urls = ["https://www.armaniturkiye.com/"]
    rules = (
        #Extract links matching /de/c/{string}-{numbers} to get all prducts of categories
        Rule(LinkExtractor(allow=(r"/collection/",))),

        #Extract links matching /de/p/{string}-{numbers} parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=(r"/products/",)), callback="parse_item", follow=True),
    )


    def parse_item(self, response):
        pass