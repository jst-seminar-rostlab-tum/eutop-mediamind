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
    FilterChain,
    URLPatternFilter,
)
from playwright.async_api import BrowserContext, Page

from app.core.languages import Language
from app.core.logger import get_logger
from app.models.article import Article, ArticleStatus
from app.models.subscription import Subscription
from app.services.web_harvester.crawler import Crawler
from app.services.web_harvester.scraper import TrafilaturaScraper

logger = get_logger(__name__)


class EuramsCrawler(Crawler):
    """Eurams Crawler for crawling articles from Eurams."""

    def __init__(
        self,
        subscription: Subscription,
    ):
        super().__init__(
            subscription=subscription,
        )
        self.tScraper = TrafilaturaScraper(
            subscription=subscription,
        )

    def is_date_in_range(
        self,
        article_date: Optional[date],
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> bool:
        """Check if the article date is within the specified range."""
        if not article_date:
            return False

        # Convert datetime to date for comparison if needed
        start_date = date_start.date() if date_start else None
        end_date = date_end.date() if date_end else None

        if start_date and article_date < start_date:
            return False

        if end_date and article_date > end_date:
            return False

        return True

    def _extract_date_from_result(self, result) -> Optional[date]:
        """Extract date from crawl result."""
        soup = BeautifulSoup(result.html, "html.parser")
        time_selector = self.subscription.login_config.get("time_selector")
        time_tag = soup.select_one(time_selector)

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

    def _process_article_result(
        self,
        result,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> Optional[Article]:
        """Process a single article result and return Article object."""
        article_date = self._extract_date_from_result(result)

        if not self.is_date_in_range(article_date, date_start, date_end):
            return None

        try:
            published_at = (
                datetime.combine(article_date, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
                if article_date
                else datetime.now(timezone.utc)
            )
            article = Article(
                url=result.url,
                published_at=published_at,
                language=Language.DE.value,
                categories=[],
                summary=None,
                status=ArticleStatus.SCRAPED,
                relevance=0,
                subscription_id=self.subscription.id,
                crawled_at=datetime.now(timezone.utc),
                scraped_at=datetime.now(timezone.utc),
            )
            return self.tScraper.extract(result.html, article)
        except Exception as e:
            logger.warning(f"Failed to process article {result.url}: {e}")
            return None

    async def _handle_cookie_consent(
        self, page: Page, context: BrowserContext, url: str, response, **kwargs
    ):
        """Handle cookie consent popup."""
        try:
            iframe_selector = self.subscription.login_config.get(
                "iframe_selector"
            )
            cookie_button_selector = self.subscription.login_config.get(
                "cookie_button_selector"
            )
            await page.wait_for_selector(iframe_selector, timeout=10000)
            iframe_element = await page.query_selector(iframe_selector)

            if iframe_element:
                frame = await iframe_element.content_frame()
                if frame:
                    await frame.click(cookie_button_selector, timeout=5000)

        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")

        return page

    def _setup_crawler_config(self) -> tuple:
        """Setup crawler configuration."""

        urlfilter = URLPatternFilter(patterns=["*nachrichten*.html"])

        browser_config = BrowserConfig(headless=True, verbose=False)

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="article",
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=1, filter_chain=FilterChain([urlfilter])
            ),
        )

        return browser_config, config

    async def _crawl_single_page(
        self,
        crawler: AsyncWebCrawler,
        page_num: int,
        config: CrawlerRunConfig,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
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
                    article = self._process_article_result(
                        result, date_start, date_end
                    )
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
            logger.warning(f"Error crawling page {page_num}: {e}")
            return [], False

    async def crawl_urls(
        self,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        limit: int = -1,
    ) -> List[Article]:
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
                crawler, page_num, config, date_start, date_end
            )

            all_articles.extend(page_articles)

            # check if any articles are out of range
            if has_out_of_range:
                logger.info(
                    f"Found articles outside date range on page {page_num}, "
                    f"stopping crawl"
                )
                should_stop = True

            if limit > 0 and len(all_articles) >= limit:
                logger.info(f"Reached article limit ({limit}), stopping crawl")
                should_stop = True

            page_num += 1

        await crawler.close()

        final_articles = all_articles[:limit] if limit > 0 else all_articles

        logger.info(
            f"Crawling completed: {len(final_articles)} articles extracted "
            f"from {page_num - 1} pages"
        )

        return final_articles


if __name__ == "__main__":
    # Example subscription ID
    subscription = Subscription(
        id=uuid.uuid4(),
        name="Example Subscription",
        paywall=False,
        domain="eurams.de",
        login_config={
            "time_selector": "body > section > div > article > header "
            "> div.article-meta > div.article-date > time",
            "iframe_selector": "iframe#sp_message_iframe_879787",
            "cookie_button_selector": "button[title='AKZEPTIEREN UND WEITER']",
        },
    )

    crawler = EuramsCrawler(
        subscription=subscription,
    )

    articles = asyncio.run(
        crawler.crawl_urls(
            date_start=datetime(2025, 7, 1), date_end=None, limit=50
        )
    )
