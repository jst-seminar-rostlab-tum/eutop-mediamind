import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling.filters import FilterChain, ContentRelevanceFilter

# Discard
relevance_filter = ContentRelevanceFilter(
    query="new laws and regulations in Europe",
    threshold=0.7
)

# Prioritize
scorer = KeywordRelevanceScorer(
    keywords=["europe", "elections", "parliament", "trading"],
    weight=0.5
)


async def scrape_with_deep_crawl(base_url, max_depth, max_pages):

    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        viewport_width=1280,
        viewport_height=720,
    )

    deep_strategy = BestFirstCrawlingStrategy(
        max_depth=max_depth,
        include_external=False,
        url_scorer=scorer,
        max_pages=max_pages,
        filter_chain=FilterChain([relevance_filter])
    )

    run_config = CrawlerRunConfig(
        deep_crawl_strategy=deep_strategy,
        word_count_threshold=0,
        exclude_external_links=True,
        remove_overlay_elements=True,
        process_iframes=True,
    )

    article_contents = {}

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(
                url=base_url,
                config=run_config
            )

            if isinstance(results, list):
                print("Scraped pages:")
                for i, result in enumerate(results):
                    if result.url.rstrip('/') != base_url.rstrip('/'):
                        print(f"- {result.url}")
                        article_contents[result.url] = result.markdown
            else:
                print("Deep crawl failed, no list of articles created")

    except Exception as e:
        print(f"Error at crawling: {e}")

    print("Crawling finalized")
    return article_contents


link = 'https://table.media/en/'
max_depth = 2
max_pages = 5
final_result = asyncio.run(scrape_with_deep_crawl(link, max_depth, max_pages))

if final_result:
    first_url = next(iter(final_result))
    first_content = final_result[first_url]
    print(first_url)
    print(first_content)
