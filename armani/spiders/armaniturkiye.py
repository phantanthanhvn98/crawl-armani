import pandas as pd
import ast
from collections import defaultdict

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from ..items import ArmaniItem

from ..utils import extract_number_from_string

class ArmaniTurkiyeSpider(CrawlSpider):
    name = "armaniturkiye"

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'armani.middlewares.ArmaniTurkiyeDownloaderMiddleware': 443,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    allowed_domains = ["armaniturkiye.com"]
    # start_urls = ["https://www.armaniturkiye.com/"]
    start_urls = ["https://www.armaniturkiye.com/collections/giyim-c-3.html?&gender=1"]
    rules = (
        #Extract links matching /de/c/{string}-{numbers} to get all prducts of categories
        Rule(LinkExtractor(allow=(r"/collections/",))),

        #Extract links matching /de/p/{string}-{numbers} parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=(r"/products/",)), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        item = ast.literal_eval(response.body.decode("utf-8"))
        product = ItemLoader(item=ArmaniItem())
        for key in item.keys():
            product.add_value(key, item[key])
        return product.load_item()