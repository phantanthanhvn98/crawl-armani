import time
import asyncio
from playwright.async_api import async_playwright, Playwright

async def extract(page, color_container, size_container):
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
    #     const  attributes = document.querySelectorAll('div.item-shop-panel__details p span.value')[0].innerText;
    #     return [detail, attributes];
    # }''')
    # sub_string = "||"
    # attributes = attributes.replace("\n", sub_string)
    # attributes = attributes[len(sub_string): ] if (attributes.startswith(sub_string)) else attributes
    # attributes = attributes[:-len(sub_string)] if (attributes.endswith(sub_string)) else attributes
    # print(f'detail: {detail} attributes: {attributes}')

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
    # print("brand: ", brand)

    #color
    color = await color_container.query_selector("#JpGrSbiUOF h3") 
    color = await color.text_content() if size else ""
    print("color: ", color.replace("\n", "").replace("\t", "").replace(" ", ""))

    #size
    size = await size_container.text_content()
    size = await size.text_content() if size else ""
    print("size: ", size.replace("\n", "").replace("\t", "").replace(" ", ""))

async def run(playwright: Playwright):
    chromium = playwright.firefox # or "firefox" or "webkit".
    browser = await chromium.launch(
        headless=True,
        ignore_https_errors=True,
        proxy={
            'server': 'http://185.198.61.66:16840',
        },
        firefox_user_prefs  = {
            'security.enterprise_roots.enabled': True
        }
    )
    await browser.new_context(ignore_https_errors=True)
    ua = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 Safari/537.36"""
    page = await browser.new_page(user_agent=ua)

    # await page.set_extra_http_headers({'Remote-Address': '185.198.61.66:16840'})
    page.set_default_timeout(60000)
    await page.goto("https://www.armaniturkiye.com/products/armani-surepellent-fullzip-allover-jacquard-eagles-siyah-sxdom1485-p-1261.html")
    # await page.goto("https://whatismyipaddress.com/")
    # time.sleep(100000)
    print("test: ", await page.content())
    cookie = page.locator("#footer_tc_privacy_button_3")
    if(await cookie.is_visible()):
        await cookie.click(force=True)
    color_containers = await page.query_selector_all('#hsPXWUmG1W') #colorInfo
    if(color_containers):
        for i, color_container in enumerate(color_containers):
            await color_container.click(force=True)
            size_containers = await page.query_selector_all('#list_1 li span')
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
