# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
import html
import math
from scrapy import signals, Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from scrapy.http import HtmlResponse, Response

from playwright.async_api import async_playwright

from .utils import ends_with_number_html, write_page, remove_spaces
from playwright.async_api import expect

expect.set_options(timeout=10_000)

class ArmaniSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ArmaniDeDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    async def process_request(self, request, spider):
        print(f'process url: {request.url}')
        async with async_playwright() as playwright:
            chromium = playwright.firefox # or "firefox" or "webkit".
            browser = await chromium.launch(headless=True)
            context = await browser.new_context(ignore_https_errors=True)
            ua = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"""
            # ua = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 Safari/537.36"""
            page = await browser.new_page(user_agent=ua)
            page.set_default_timeout(180000)
            await page.goto(request.url)
            if(ends_with_number_html(request.url)):
                print(f'********** Its product page: {request.url}')
                result = await self.click_colors_sizes(page)
                page_content = str(result)
            else:
                print(f'********** Its not a product page: {request.url}')
                page_content = await page.content()

            # other actions...
            await browser.close()
        return HtmlResponse(
            request.url,
            body= page_content.encode('utf-8'),
            encoding='utf-8',
            request=request
        )

    async def click_colors_sizes(self, page):
        data = []
        await page.locator("#footer_tc_privacy_button_3").click()
        color_containers = await page.query_selector_all('.colorInfo') #colorInfo
        size_containers = await page.query_selector_all('//li[not(contains(@class, "is-disabled"))]//label[contains(@class, "sizeInfo")]')
        if(color_containers and size_containers):
            for color_container in color_containers:
                size_containers = await page.query_selector_all('//li//label[contains(@class, "sizeInfo")]')
                if(await color_container.is_visible()):
                    await color_container.click(force=True)
                    if(size_containers):
                        for size_container in size_containers:
                            if(await size_container.is_visible()):
                                await size_container.click(force=True)
                                data.append(await self.extract(page, color_container, size_container))
                elif(size_containers):
                    for size_container in size_containers:
                        if(await size_container.is_visible()):
                            await size_container.click(force=True)
                            data.append(await self.extract(page, None, size_container))
        elif(color_containers and not size_containers):
            for color_container in color_containers:
                if(await color_container.is_visible()):
                    await color_container.click(force=True)
                    data.append(await self.extract(page, color_container, None))
        elif(not color_containers and size_containers):
            for size_container in size_containers:
                if(await size_container.is_visible()):
                    await size_container.click(force=True)
                    data.append(await self.extract(page, None, size_container))
        size_containers = await page.query_selector_all('#makeupColorsContent li a div.label')
        size_url = await page.evaluate_handle('''() => {
            const links = Array.from(document.querySelectorAll('#makeupColorsContent li a'));
            return links.map(link => link.getAttribute('href'));
        }''')
        size_url = await size_url.json_value() if size_url else None
        if(size_containers):
            size_container = await page.query_selector('#makeupColorsContent li div div.label')
            data.append(await self.extract(page, None, size_container))
            for i, size_container in enumerate(size_containers):
                if(await size_container.is_visible()):
                    await size_container.click(force=True)
                    await page.wait_for_url(f'**/{size_url[i].split("/")[-1]}')
                    data.append(await self.extract(page, None, size_container))
        elif(len(data) < 1):
            data.append(await self.extract(page, None, None))

        return data

    async def extract(self, page, color_container, size_container):
         #url
        url = page.url

        #code
        sku = await page.query_selector('//div[contains(@class, "item-shop-panel__modelfabricolor")]//p//span[contains(@class, "value")]')
        sku = await code.inner_html() if code is not None else ""
        print("code: ", sku)

        #name 
        name = await page.query_selector('.item-shop-panel__name')
        name = await name.inner_html() if name is not None else ""
        name = name.replace("\n", "").replace("\t", "").replace(" ", "")
        print("name: ", name)

        #description
        description = await page.query_selector('//div[contains(@class, "item-shop-panel__description")]//p//span[contains(@class, "value")]')
        description = await description.inner_html() if description is not None else ""
        print("description: ", description)

        #image_urls
        image_urls = await page.evaluate('''() => {
            const images = document.querySelectorAll('ul.swiper-wrapper li div.image img');
            return Array.from(images).map(img => img.src);
        }''')
        image_urls = ",".join(image_urls[int(len(image_urls)/2):]) if image_urls is not None else ""
        print("image_urls: ", image_urls)

        #detail, attributes
        (detail, attributes) = await page.evaluate('''() => {
            let details = document.querySelectorAll('div.item-shop-panel__details p');
            detail = details.length > 0 ? details[0].innerText : "";
            const substr = "||";
            const  attributes = document.querySelectorAll('div.item-shop-panel__details p span.value')[0].innerText.replaceAll("&nbsp;", " ");
            return [detail, attributes];
        }''')
        sub_string = "||"
        attributes = attributes.replace("\n", sub_string)
        attributes = attributes.replace(": ", "##").replace(":", "##")
        attributes = attributes[len(sub_string): ] if (attributes.startswith(sub_string)) else attributes
        attributes = html.unescape(attributes[:-len(sub_string)] if (attributes.endswith(sub_string)) else attributes)
        print(f'detail: {detail} attributes: {attributes}')

        #breadcrumbs
        breadcrumbs = await page.evaluate('''() => {
            const breadcrumbs = [ ...document.querySelectorAll('ul.breadcrumbs li a span.text'), ...document.querySelectorAll('ul.breadcrumbs li span span.text')];
            return Array.from(breadcrumbs).map(breadcrumb => breadcrumb.innerText);
        }''')

        #category
        category = breadcrumbs[-2] if len(breadcrumbs) > 0 else ""
        print("category: ", category)

        breadcrumbs = ">".join(breadcrumbs)
        print("breadcrumbs: ", breadcrumbs)
        
        #price
        price = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('div.itemPrice span.price span')).slice(0, 2).map((item) => item.innerText).join(" ");
        }''')
        print("price: ", price)

        #brand
        brand = await page.evaluate('''() => {
            return document.querySelector('p.item-shop-panel__brand').innerText;
        }''')
        print("brand: ", brand)

        #color
        color =  "" if color_container is None else await color_container.text_content()
        color = remove_spaces(color)
        print("color: ", color)

        #size
        size = "" if size_container is None else await size_container.text_content()
        size = remove_spaces(size)
        print("size: ", size)
        return {
            "sku": sku,
            "url": url,
            "name": name,
            "description": description,
            "image_urls": image_urls,
            "details": detail,
            "attributes": attributes,
            "breadcrumbs": breadcrumbs,
            "category": category,
            "price": price,
            "brand": brand,
            "color": color,
            "size": size
        }

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class ArmaniTurkiyeDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    async def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        print(f'process url: {request.url}')
        async with async_playwright() as playwright:
            chromium = playwright.firefox # or "firefox" or "webkit".
            browser = await chromium.launch(headless=True)
            await browser.new_context(ignore_https_errors=True)
            ua = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"""
            # ua = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 Safari/537.36"""
            page = await browser.new_page(user_agent=ua)
            page.set_default_timeout(1800000)
            await page.goto(request.url, timeout=1800000)
            if(ends_with_number_html(request.url)):
                print(f'********** Its product page: {request.url}')
                result = await self.click_colors_sizes(page)
                page_content = str(result)
            else:
                print(f'********** Its not a product page: {request.url}')
                page = await self.infinity_scroll(page)
                page_content = await page.content()

            # other actions...
            await browser.close()
        return HtmlResponse(
            request.url,
            body= page_content.encode('utf-8'),
            encoding='utf-8',
            request=request
        )

    async def click_colors_sizes(self, page):
        data = []
        cookie = page.locator("#footer_tc_privacy_button_3")
        if(await cookie.is_visible()):
            await cookie.click(force=True)

        color_containers = await page.query_selector_all('#hsPXWUmG1W') 
        size_containers = await page.query_selector_all('ul.list_attribute li span')
        if(color_containers and size_containers):
            for color_container in color_containers:
                size_containers = await page.query_selector_all('ul.list_attribute li span')
                if(await color_container.is_visible()):
                    await color_container.click(force=True)
                    if(size_containers):
                        for size_container in size_containers:
                            if(await size_container.is_visible()):
                                await size_container.click(force=True)
                                data.append(await self.extract(page, color_container, size_container))
                elif(size_containers):
                    for size_container in size_containers:
                        if(await size_container.is_visible()):
                            await size_container.click(force=True)
                            data.append(await self.extract(page, None, size_container))
        elif(color_containers and not size_containers):
            for color_container in color_containers:
                if(await color_container.is_visible()):
                    await color_container.click(force=True)
                    data.append(await self.extract(page, color_container, None))
        elif(not color_containers and size_containers):
            for size_container in size_containers:
                if(await size_container.is_visible()):
                    await size_container.click(force=True)
                    data.append(await self.extract(page, None, size_container))
        # size_containers = await page.query_selector_all('#makeupColorsContent li a div.label')
        # size_url = await page.evaluate_handle('''() => {
        #     const links = Array.from(document.querySelectorAll('#makeupColorsContent li a'));
        #     return links.map(link => link.getAttribute('href'));
        # }''')
        # size_url = await size_url.json_value() if size_url else None
        # if(size_containers):
        #     size_container = await page.query_selector('#makeupColorsContent li div div.label')
        #     data.append(await self.extract(page, None, size_container))
        #     for i, size_container in enumerate(size_containers):
        #         if(await size_container.is_visible()):
        #             await size_container.click(force=True)
        #             await page.wait_for_url(f'**/{size_url[i].split("/")[-1]}')
        #             data.append(await self.extract(page, None, size_container))
        if(len(data) < 1):
            data.append(await self.extract(page, None, None))

        return data

    async def infinity_scroll(self, page):
        previous_height = await page.evaluate('document.body.scrollHeight')
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.waitForLoadState('networkidle')
            current_height = await page.evaluate('document.body.scrollHeight')
            if current_height == previous_height:
                break
            previous_height = current_height
        return page

    async def extract(self, page, color_container, size_container):
        #url
        url = page.url

        #code
        sku = await page.query_selector('//div[contains(@class, "products_model")]')
        sku = await sku.inner_html() if sku is not None else "" 
        print("sku: ", sku)

        #name 
        name = await page.query_selector('#productName')
        name = await name.inner_html()
        print("name: ", name)

        #description
        description = await page.query_selector('#hJTWbtVF5K')
        description = await description.inner_html()
        print("description: ", description)

        #image_urls
        image_urls = await page.evaluate('''() => {
            const images = document.querySelectorAll('div.slick-track div div img');
            return [...new Set(Array.from(images).map(img => img.src))]
        }''')
        image_urls = ','.join(image_urls) if image_urls is not None else ""
        print("image_urls: ", image_urls)

        #detail, attributes
        # (detail, attributes) = await page.evaluate('''() => {
        #     let details = document.querySelectorAll('div.item-shop-panel__details p');
        #     detail = details.length > 0 ? details[0].innerText : "";
        #     const substr = "||";
        #     const  attributes = document.querySelectorAll('div.item-shop-panel__details p span.value')[0].innerText.replaceAll("&nbsp;", " ");
        #     return [detail, attributes];
        # }''')
        # sub_string = "||"
        # attributes = attributes.replace("\n", sub_string)
        # attributes = attributes.replace(": ", "##").replace(":", "##")
        # attributes = attributes[len(sub_string): ] if (attributes.startswith(sub_string)) else attributes
        # attributes = html.unescape(attributes[:-len(sub_string)] if (attributes.endswith(sub_string)) else attributes)
        # print(f'detail: {detail} attributes: {attributes}')
        (detail, attributes) = ("", "")

        #breadcrumbs
        breadcrumbs = await page.evaluate('''() => {
            const breadcrumbs = document.querySelectorAll('div.sUGt28rEGB a');
            return Array.from(breadcrumbs).map(breadcrumb => breadcrumb.innerText);
        }''')

        #category
        category = breadcrumbs[-1] if len(breadcrumbs) > 0 else ""
        print("category: ", category)

        breadcrumbs = ">".join(breadcrumbs)
        print("breadcrumbs: ", breadcrumbs)
        
        #price
        price = await page.query_selector('div.productSpecialPrice')
        price = price.text_content() if price is not None else ""
        print("price: ", price)

        #brand
        # brand = await page.evaluate('''() => {
        #     return document.querySelector('p.item-shop-panel__brand').innerText;
        # }''')
        brand = ""
        print("brand: ", brand)

        #color
        color = await color_container.query_selector("#JpGrSbiUOF h3") 
        color = await color.text_content() if size else ""
        print("color: ", color.replace("\n", "").replace("\t", "").replace(" ", ""))

        #size
        size = await size_container.text_content()
        size = await size.text_content() if size else ""
        print("size: ", size.replace("\n", "").replace("\t", "").replace(" ", ""))
        
        return {
            "sku": sku,
            "url": url,
            "name": name,
            "description": description,
            "image_urls": image_urls,
            "details": detail,
            "attributes": attributes,
            "breadcrumbs": breadcrumbs,
            "category": category,
            "price": price,
            "brand": brand,
            "color": color,
            "size": size
        }
        pass 

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
