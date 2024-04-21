import ast
import math
import pandas as pd
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy import Request


from ..items import ArmaniItem
from ..utils import ends_with_number_html, extract_number_from_string

PAGE_SIZE = 36


class ArmaniDeSpider(CrawlSpider):
    name = "armanide"

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'armani.middlewares.ArmaniDeDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        }
    }

    allowed_domains = ["www.armani.com"]
    start_urls = ["https://www.armani.com/de-de/"]
    
    rules = (
        Rule(LinkExtractor(allow=r'\d+\.html$'), callback="parse_item", follow=True),
        Rule(LinkExtractor(allow=r'/de-de/'), callback="parse_pages", follow=True),
    )

    def parse_pages(self, response):
        print(f'call back parse_pages: {response.url}')
        # check if have pageable 
        totalProducts = response.xpath('//span[@class="totalQuantity"]/text()').get()
        partialProducts = response.xpath('//span[@class="partialQuantity"]/text()').get()
        if(totalProducts and partialProducts):
            totalProducts = int(totalProducts)
            partialProducts = int(partialProducts)
            if(partialProducts == PAGE_SIZE and totalProducts > PAGE_SIZE):
                for i in range(math.ceil(totalProducts/PAGE_SIZE) - 1):
                    print(f'*******find pages in: {response.url} {totalProducts} {partialProducts} {i+2}')
                    yield Request(f'{response.url}?page={i+2}', callback= self.parse_pages)
            elif(partialProducts > PAGE_SIZE):
                links = response.xpath('//a[contains(@class, "item-card__img-link")]/@href').extract()
                for link in links:
                    print(f'get products for next pages: ${link}')
                    yield Request(link, callback= self.parse_item)

    def parse_item(self, response):
        LOGGER.info(f'call back parse_item: {response.url}')
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
            product = ItemLoader(item=ArmaniItem())
            for key in item.keys():
                product.add_value(key, item[key])
            yield product.load_item()