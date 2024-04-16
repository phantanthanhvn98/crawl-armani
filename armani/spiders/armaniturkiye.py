import ast
from collections import defaultdict

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
        data = ast.literal_eval(response.body.decode("utf-8"))

        merged_data = defaultdict(lambda: {"image_urls": [], "price": None})

        for item in data:
            url = item["url"]
            merged_data[url]["image_urls"].extend(item["image_urls"].split(","))
            if merged_data[url]["price"] is None:
                merged_data[url]["price"] = item["price"]

        final_result = [{"url": url, "image_urls": "#".join(info["image_urls"]), "price": info["price"]} for url, info in merged_data.items()]

        for item in final_result:
            product = ItemLoader(item=ArmaniItem())
            for key in item.keys():
                product.add_value(key, item[key])
            yield product.load_item()