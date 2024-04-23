import pandas as pd
import ast
import math
import json
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy import Request


from ..items import ArmaniItem
from ..utils import ends_with_number_html, extract_number_from_string


class ArmaniDeSpider(Spider):
    name = "armanide-error"

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'armani.middlewares.ArmaniDeDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    allowed_domains = ["www.armani.com"]


    start_urls = []
    f = open('file.log', 'r')
    str = f.read()
    str = str.split("ERROR: Error downloading <GET ")
    for i in str:
        url = i.split(">")[0]
        if url.startswith("https://") and url.endswith(".html"):
            start_urls.append(url)
    print("start url length: ", len(start_urls))

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_custom)

    def parse_item(self, response):
        item = ast.literal_eval(response.body.decode("utf-8"))
        product = ItemLoader(item=ArmaniItem())
        for key in item.keys():
            product.add_value(key, item[key])
        return product.load_item()