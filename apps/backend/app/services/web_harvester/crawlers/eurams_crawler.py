import asyncio
import json
import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from bs4 import BeautifulSoup
from crawl4ai import (
    AsyncWebCrawler,
    BFSDeepCrawlStrategy,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    FilterChain,
    JsonCssExtractionStrategy,
    PruningContentFilter,
    URLPatternFilter,
)
from playwright.async_api import BrowserContext, Page

from app.core.languages import Language
from app.core.logger import get_logger
from app.models.article import Article, ArticleStatus

logger = get_logger(__name__)


class EuramsCrawler:
    """Eurams Crawler for crawling articles from Eurams."""

    TIME_SELECTOR = (
        "body > section > div > article > header > "
        "div.article-meta > div.article-date > time"
    )
    IFRAME_SELECTOR = "iframe#sp_message_iframe_879787"
    COOKIE_BUTTON_SELECTOR = "button[title='AKZEPTIEREN UND WEITER']"

    def __init__(
        self,
        subscription_id: uuid.UUID,
        date_start: Optional[date] = None,
        date_end: Optional[date] = None,
        limit: int = -1,
        language: str = Language.DE.value,
    ):
        self.subscription_id = subscription_id
        self.date_start = date_start
        self.date_end = date_end
        self.limit = limit
        self.language = language

    def is_date_in_range(self, article_date: Optional[date]) -> bool:
        """Check if the article date is within the specified range."""
        if not article_date:
            return False

        if self.date_start and article_date < self.date_start:
            return False

        if self.date_end and article_date > self.date_end:
            return False

        return True

    def _get_extraction_schema(self) -> dict:
        """Get the extraction schema for articles."""
        return {
            "name": "Eurams Article Schema",
            "baseSelector": "body > section > div > article",
            "fields": [
                {"name": "title", "selector": "header > h1", "type": "text"},
                {
                    "name": "author",
                    "selector": "header .article-meta .article-author strong",
                    "type": "text",
                },
                {
                    "name": "published_at",
                    "selector": "header .article-meta .article-date time",
                    "type": "text",
                },
                {
                    "name": "content",
                    "selector": "div > div > div",
                    "type": "text",
                },
                {
                    "name": "image_url",
                    "selector": "header > div:nth-child(3) > figure > "
                    "picture > img",
                    "type": "attribute",
                    "attribute": "src",
                },
            ],
        }

    def _extract_date_from_result(self, result) -> Optional[date]:
        """Extract date from crawl result."""
        soup = BeautifulSoup(result.html, "html.parser")
        time_tag = soup.select_one(self.TIME_SELECTOR)

        if not time_tag:
            logger.warning(f"No date tag found for URL: {result.url}")
            return None

        # try to extract date from datetime attribute
        datetime_attr = time_tag.get("datetime")
        if datetime_attr:
            try:
                article_date = datetime.fromisoformat(
                    datetime_attr.split("T")[0]
                ).date()
                return article_date
            except ValueError as e:
                logger.warning(
                    f"Failed to parse date from datetime attr: "
                    f"{datetime_attr}, error: {e}"
                )

        # use text content as fallback
        date_text = time_tag.get_text(strip=True)
        logger.warning(
            f"Could not extract date from datetime attr, "
            f"found text: {date_text}"
        )
        return None

    def _extract_article_data(self, result) -> Optional[dict]:
        """Extract structured data from crawl result."""
        try:
            data = (
                json.loads(result.extracted_content)
                if result.extracted_content
                else []
            )
            return data[0] if data else {}
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(
                f"Failed to extract article data from {result.url}: {e}"
            )
            return {}

    def _process_article_result(self, result) -> Optional[Article]:
        """Process a single article result and return Article object."""
        article_date = self._extract_date_from_result(result)

        if not self.is_date_in_range(article_date):
            return None

        try:
            extracted_data = self._extract_article_data(result)

            content = (
                result.markdown.fit_markdown
                if result.markdown.fit_markdown
                else result.markdown.raw_markdown
            )

            title = (
                extracted_data.get("title", "").strip() or "Untitled Article"
            )

            author_text = extracted_data.get("author", "").strip()
            authors = [author_text] if author_text else []

            image_url = extracted_data.get("image_url", "").strip() or None

            published_at = (
                datetime.combine(article_date, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
                if article_date
                else datetime.now(timezone.utc)
            )

            article = Article(
                title=title,
                content=content,
                url=result.url,
                image_url=image_url,
                authors=authors,
                published_at=published_at,
                language=self.language,
                categories=[],
                summary=None,
                status=ArticleStatus.SCRAPED,
                relevance=0,
                subscription_id=self.subscription_id,
                crawled_at=datetime.now(timezone.utc),
                scraped_at=datetime.now(timezone.utc),
            )

            return article

        except Exception as e:
            logger.error(f"Failed to process article {result.url}: {e}")
            return None

    async def _handle_cookie_consent(
        self, page: Page, context: BrowserContext, url: str, response, **kwargs
    ):
        """Handle cookie consent popup."""
        try:
            await page.wait_for_selector(self.IFRAME_SELECTOR, timeout=10000)
            iframe_element = await page.query_selector(self.IFRAME_SELECTOR)

            if iframe_element:
                frame = await iframe_element.content_frame()
                if frame:
                    await frame.click(
                        self.COOKIE_BUTTON_SELECTOR, timeout=5000
                    )

        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")

        return page

    def _setup_crawler_config(self) -> tuple:
        """Setup crawler configuration."""
        prune_filter = PruningContentFilter(
            threshold=0.45, threshold_type="dynamic", min_word_threshold=5
        )

        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

        urlfilter = URLPatternFilter(patterns=["*nachrichten*.html"])

        browser_config = BrowserConfig(headless=True, verbose=False)

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="article",
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=1, filter_chain=FilterChain([urlfilter])
            ),
            extraction_strategy=JsonCssExtractionStrategy(
                self._get_extraction_schema()
            ),
            markdown_generator=md_generator,
        )

        return browser_config, config

    async def _crawl_single_page(
        self, crawler: AsyncWebCrawler, page_num: int, config: CrawlerRunConfig
    ) -> tuple[List[Article], bool]:
        """Crawl a single page and return Article objects
        and whether to stop."""
        url = f"https://www.eurams.de/nachrichten/{page_num}"

        try:
            results = await crawler.arun(url, config=config)
            page_articles = []
            has_out_of_range_article = False

            for result in results:
                if result.success:
                    article = self._process_article_result(result)
                    if article:
                        page_articles.append(article)
                    else:
                        has_out_of_range_article = True
                else:
                    logger.warning(
                        f"Failed to crawl {result.url}: "
                        f"{result.error_message}"
                    )

            return page_articles, has_out_of_range_article

        except Exception as e:
            logger.error(f"Error crawling page {page_num}: {e}")
            return [], False

    async def crawl_urls_async(self) -> List[Article]:
        """Main crawling method that returns List[Article]."""
        logger.info("Starting Eurams crawling process")

        browser_config, config = self._setup_crawler_config()
        crawler = AsyncWebCrawler(config=browser_config)

        # only handle cookie consent on the first load
        is_first_load = True

        async def after_goto_wrapper(*args, **kwargs):
            nonlocal is_first_load
            if is_first_load:
                result = await self._handle_cookie_consent(*args, **kwargs)
                is_first_load = False
                return result
            else:
                return args[0]  # return page

        crawler.crawler_strategy.set_hook("after_goto", after_goto_wrapper)
        await crawler.start()

        all_articles: List[Article] = []
        page_num = 1
        max_pages = 30
        should_stop = False

        while page_num <= max_pages and not should_stop:
            page_articles, has_out_of_range = await self._crawl_single_page(
                crawler, page_num, config
            )

            all_articles.extend(page_articles)

            # check if any articles are out of range
            if has_out_of_range:
                logger.info(
                    f"Found articles outside date range on page {page_num}, "
                    f"stopping crawl"
                )
                should_stop = True

            if self.limit > 0 and len(all_articles) >= self.limit:
                logger.info(
                    f"Reached article limit ({self.limit}), stopping crawl"
                )
                should_stop = True

            page_num += 1

        await crawler.close()

        final_articles = (
            all_articles[: self.limit] if self.limit > 0 else all_articles
        )

        logger.info(
            f"Crawling completed: {len(final_articles)} articles extracted "
            f"from {page_num - 1} pages"
        )

        return final_articles


if __name__ == "__main__":
    # Example subscription ID
    subscription_id = uuid.uuid4()

    crawler = EuramsCrawler(
        subscription_id=subscription_id,
        date_start=date(2025, 6, 15),
        date_end=None,
        limit=50,
        language=Language.DE.value,
    )

    articles = asyncio.run(crawler.crawl_urls_async())
