import asyncio
import json
import os
import uuid
from typing import Any, List

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    RateLimiter,
)
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.content_filter_strategy import (
    BM25ContentFilter,
    PruningContentFilter,
)
from crawl4ai.extraction_strategy import (
    CosineStrategy,
    JsonCssExtractionStrategy,
)
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

urls = [
    "https://www.ft.com/content/c779b3b6-e989-4277-91fd-d724682918be",
    "https://www.ft.com/content/03c86b1c-5563-4879-a9ab-78a576f9f474",
    # "https://www.handelsblatt.com/politik/international/kriegsschiff-nordkoreas-werftarbeiter-richten-gekenterten-zerstoerer-wieder-auf/100133717.html",
    # "https://www.handelsblatt.com/finanzen/banken-versicherungen/trade-republic-was-sollten-sie-als-kunde-des-neobrokers-beachten/100070689.html",
]
# strategy = CosineStrategy(
#     semantic_filter="main article content",
#     word_count_threshold=100,  # Longer blocks for articles
# )

# bm25_filter = BM25ContentFilter(
#         user_query="News articles without unreadable content",
#         # Adjust for stricter or looser results
#         bm25_threshold=1.2
#     )

dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=90.0,  # Pause if memory exceeds this
    check_interval=1.0,  # How often to check memory
    max_session_permit=1,  # Maximum concurrent tasks
    rate_limiter=RateLimiter(  # Optional rate limiting
        base_delay=(2.0, 3.0), max_delay=30.0, max_retries=2
    ),
    # monitor=CrawlerMonitor(         # Optional monitoring
    #     urls_total=len(urls),
    #     display_mode=DisplayMode.DETAILED
    # )
)

# Create a pruning filter
prune_filter = PruningContentFilter(
    # Lower → more content retained, higher → more content pruned
    threshold=0.4,
    # "fixed" or "dynamic"
    threshold_type="dynamic",
    # Ignore nodes with <10 words
    min_word_threshold=10,
)


# Insert it into a Markdown Generator
md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

# Use the login identity
browser_config = BrowserConfig(
    use_managed_browser=True,
    user_data_dir="~/ChromeCache/",
    browser_type="chromium",
    headless=True,
    verbose=True,
    light_mode=True,
)


crawl_config = CrawlerRunConfig(
    scan_full_page=True,
    page_timeout=60000,
    markdown_generator=md_generator,
    cache_mode=CacheMode.BYPASS,
    stream=False,
    log_console=True,
)


async def process_urls(urls: List[str]) -> List[Any]:
    final_results = []
    # output_dir = "extracted_jsons"
    # os.makedirs(output_dir, exist_ok=True)

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()
    
    # crawl_config.session_id = str(uuid.uuid4())
    async for result in await crawler.arun_many(urls, config=crawl_config):
        if result.success:
            final_results.append(result)
            print(f"✅ Extracted {result.url} with {len(result.extracted_content)} characters")
        else:
            final_results.append({"url": result.url, "error": result.error_message})
            print(f"❌ Failed to extract {result.url}: {result.error_message}")
    # if result.success and result.extracted_content:
    #     try:
    #         data = json.loads(result.extracted_content)
    #         filename = f"article_{len(results)}.json"
    #         with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
    #             json.dump(data, f, ensure_ascii=False, indent=2)
    #         results.append({"url": result.url, "file": filename})
    #         print(f"✅ Saved {result.url} → {filename}")
    #     except Exception as e:
    #         results.append({"url": result.url, "error": f"JSON parse error: {e}"})
    #         print(f"❌ Parse error for {result.url}: {e}")
    # else:
    #     results.append({"url": result.url, "error": result.error_message})
    #     print(f"❌ Failed to extract {result.url}: {result.error_message}")

    await crawler.close()

    return final_results


async def main():
    # process urls from test_urls.json
    # with open("backend/app/services/test_urls.json", "r", encoding="utf-8") as f:
    #     urls = json.load(f)
    # asyncio.run(process_urls(urls))
    # print the results
    results = await process_urls(urls)
    for result in results:
        if result.success:
            print(result.markdown.fit_markdown)


if __name__ == "__main__":
    asyncio.run(main())
