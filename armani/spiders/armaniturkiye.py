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
        print(f'call back parse_item: {response.url}')
        df = pd.DataFrame(ast.literal_eval(response.body.decode("utf-8")))
        df = df[df['url'] != 'url']
        df['price'] = df['price'].astype(str)
        df['size'] = df['size'].astype(str).apply(lambda x: extract_number_from_string(x))
        df['color'] = df['color'].astype(str)
        df['image_urls'] = df['image_urls'].apply(lambda x: ','.join([item for item in x.split(',') if not item.endswith('.html')]))
        df['category'] = df['breadcrumbs'].apply(lambda x: x.split(">")[-1])
        grouped_df = df.groupby('url').agg(
            {
                'price': '#'.join, 
                'image_urls': '#'.join, 
                'color': '#'.join,
                'size': '#'.join,
                "code": "first",
                "name": "first",
                "description": "first",
                "category": "first",
                "brand": "first",
                "details": "first",
                "breadcrumbs": "first",
                "attributes": "first"
            }
        ).reset_index()

        grouped_df['image_urls'] = grouped_df['image_urls'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

        grouped_df['price'] = grouped_df['price'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

        grouped_df['size'] = grouped_df['size'].apply(lambda x: '#'.join(set(x.split("#"))))
        grouped_df['color'] = grouped_df['color'].apply(lambda x: "#".join(set(x.replace('FürdieausgewählteGrößeistdieFarbenichterhältlich', '').split("#"))))
        grouped_df['breadcrumbs'] = grouped_df['breadcrumbs'].apply(lambda x: ">".join(x.split(">")[:-2]))
        grouped_df['category'] = grouped_df['breadcrumbs'].apply(lambda x: x.split(">")[-1])
        grouped_df['size'] = grouped_df['size'].apply(lambda x: '#'.join(set([ extract_number_from_string(value) for value in x.split("#")])))
        for item in grouped_df.to_dict('records'):
            product = ItemLoader(item=ArmaniItem())
            for key in item.keys():
                product.add_value(key, item[key])
            yield product.load_item()