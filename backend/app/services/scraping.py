import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig


async def scrape(link):
    browser_config = BrowserConfig(
        verbose=True,
        headless=False,
        viewport_width=1280,
        viewport_height=720
    )

    run_config = CrawlerRunConfig(
        # only_text=False,
        word_count_threshold=0,
        exclude_external_links=False,
        remove_overlay_elements=True,
        process_iframes=True,
        # js_code="return document.documentElement.outerHTML;",
        # js_only=True,
        # wait_until="domcontentloaded",
        # delay_before_return_html=1.0
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=link,
            config=run_config
        )
        print(result.html)


link = 'https://table.media/en/'
asyncio.run(scrape(link))
# help(CrawlerRunConfig)

# DIRECT LINK TO ARTICLE IMPLEMENTATION
