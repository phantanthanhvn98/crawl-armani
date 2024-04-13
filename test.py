import time
import asyncio
from playwright.async_api import async_playwright, Playwright

async def extract(page, color_container, size_container):
    #url
    url = page.url

    #code
    code = await page.query_selector('//div[contains(@class, "item-shop-panel__modelfabricolor")]//p//span[contains(@class, "value")]')
    code = await code.inner_html()
    print("code: ", code)

    #name 
    name = await page.query_selector('.item-shop-panel__name')
    name = await name.inner_html()
    print("name: ", name)

    #description
    description = await page.query_selector('//div[contains(@class, "item-shop-panel__description")]//p//span[contains(@class, "value")]')
    description = await description.inner_html()
    print("description: ", description)

    #image_urls
    image_urls = await page.evaluate('''() => {
        const images = document.querySelectorAll('ul.swiper-wrapper li div.image img');
        return Array.from(images).map(img => img.src);
    }''')
    image_urls = image_urls[int(len(image_urls)/2):]
    print("image_urls: ", image_urls)

    #detail, attributes
    (detail, attributes) = await page.evaluate('''() => {
        let details = document.querySelectorAll('div.item-shop-panel__details p');
        detail = details.length > 0 ? details[0].innerText : "";
        const substr = "||";
        const  attributes = document.querySelectorAll('div.item-shop-panel__details p span.value')[0].innerText;
        return [detail, attributes];
    }''')
    sub_string = "||"
    attributes = attributes.replace("\n", sub_string)
    attributes = attributes[len(sub_string): ] if (attributes.startswith(sub_string)) else attributes
    attributes = attributes[:-len(sub_string)] if (attributes.endswith(sub_string)) else attributes
    print(f'detail: {detail} attributes: {attributes}')

    #breadcrumbs
    breadcrumbs = await page.evaluate('''() => {
        const breadcrumbs = [ ...document.querySelectorAll('ul.breadcrumbs li a span.text'), ...document.querySelectorAll('ul.breadcrumbs li span span.text')];
        return Array.from(breadcrumbs).map(breadcrumb => breadcrumb.innerText);
    }''')

    #category
    category = breadcrumbs[-1] if len(breadcrumbs) > 0 else ""
    print("category: ", category)

    breadcrumbs = ">".join(breadcrumbs)
    print("breadcrumbs: ", breadcrumbs)
    

    #price
    price = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('div.itemPrice span.price span')).map((item) => item.innerText).join(" ");
    }''')
    print("price: ", price)

    #brand
    brand = await page.evaluate('''() => {
        return document.querySelector('p.item-shop-panel__brand').innerText;
    }''')
    print("brand: ", brand)

    #color
    color = await color_container.text_content()
    print("color: ", color.replace("\n", "").replace("\t", "").replace(" ", ""))

    #size
    size = await size_container.text_content()
    print("size: ", size.replace("\n", "").replace("\t", "").replace(" ", ""))

async def run(playwright: Playwright):
    chromium = playwright.firefox # or "firefox" or "webkit".
    browser = await chromium.launch(headless=False)
    context = await browser.new_context(ignore_https_errors=True)
    ua = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"""
    page = await browser.new_page(user_agent=ua)
    page.set_default_timeout(60000)
    await page.goto("https://www.armani.com/de-de/mokassins-aus-leder-mit-hirschprint_cod1647597330535429.html")
    await page.locator("#footer_tc_privacy_button_3").click()
    color_containers = await page.query_selector_all('.colorInfo') #colorInfo
    if(color_containers):
        for i, color_container in enumerate(color_containers):
            await color_container.click(force=True)
            size_containers = await page.query_selector_all('//li[not(contains(@class, "is-disabled"))]//label[contains(@class, "sizeInfo")]')
            if(size_containers):
                for size_container in size_containers:
                    await size_container.click(force=True)
                    await extract(page, color_container, size_container)

    # other actions...
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())
