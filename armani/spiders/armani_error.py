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

    def parse_custom(self, response):
        print(f'call back parse_item: {response.url}')
        print("******************************************")
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
                "sku": "first",
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
            print("**** item***", item)
            product = ItemLoader(item=ArmaniItem())
            for key in item.keys():
                product.add_value(key, item[key])
            yield product.load_item()