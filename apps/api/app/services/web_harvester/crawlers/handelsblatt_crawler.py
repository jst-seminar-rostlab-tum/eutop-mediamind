import asyncio
import uuid
from datetime import datetime, timezone
from typing import List

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from playwright.async_api import BrowserContext, Page

from app.core.logger import get_logger
from app.models.article import Article, ArticleStatus
from app.models.subscription import Subscription
from app.services.web_harvester.crawler import NewsAPICrawler

logger = get_logger(__name__)


class HandelsblattCrawler(NewsAPICrawler):

    def __init__(
        self,
        subscription: Subscription,
        sourceUri: str,
        include_blogs: bool = False,
        filter_category: bool = True,
    ):
        super().__init__(
            subscription=subscription,
            sourceUri=sourceUri,
            include_blogs=include_blogs,
            filter_category=filter_category,
        )
        self.loged_in = False

    async def _handle_cookie_consent(self, page: Page, login_config: dict):
        try:
            await page.wait_for_load_state("networkidle")
            container_count = await page.locator(
                login_config.get("container_selector")
            ).count()

            if container_count == 0:
                logger.info("No cookie consent container found, proceeding...")
                return True

            await page.wait_for_selector(
                login_config.get("iframe"), timeout=5000
            )
            iframe_element = await page.query_selector(
                login_config.get("iframe")
            )

            if iframe_element:
                frame = await iframe_element.content_frame()
                if frame:
                    await frame.wait_for_load_state(
                        "domcontentloaded", timeout=10000
                    )
                    await asyncio.sleep(2)

                    await frame.click(
                        login_config.get("cookies_button"), timeout=3000
                    )
                    logger.info("Cookie consent accepted")
                    return True
        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")

        return True

    async def _perform_login(self, page: Page, login_config: dict):
        try:
            logger.info("Starting login process...")

            await self._handle_cookie_consent(page, login_config)
            await page.wait_for_selector(
                login_config.get("user_input"), timeout=5000
            )
            await page.fill(
                login_config.get("user_input"), subscription.username
            )

            await page.fill(
                login_config.get("password_input"), subscription.secrets
            )

            await page.click(login_config.get("submit_button"), force=True)
            await page.wait_for_timeout(2000)
            logger.info("Login process completed")
            self.loged_in = True
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def _setup_crawler_config(self):
        prune_filter = PruningContentFilter(
            threshold=0.45, threshold_type="dynamic", min_word_threshold=5
        )
        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

        browser_config = BrowserConfig(
            headless=False,
            verbose=True,
        )

        config = CrawlerRunConfig(
            markdown_generator=md_generator,
            session_id=str(uuid.uuid4()),
        )

        return browser_config, config

    async def crawl_urls(
        self,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        limit: int = -1,
    ) -> List[Article]:
        browser_config, config = self._setup_crawler_config()
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.start()

        async def login_wrapper(
            page: Page, context: BrowserContext, url: str = None, **kwargs
        ):
            if not self.loged_in:
                await self._perform_login(page, self.subscription.login_config)
            return page

        crawler.crawler_strategy.set_hook("after_goto", login_wrapper)
        await crawler.arun(self.subscription.domain, config=config)
        logger.info("Calling super().crawl_urls...")
        articles = super().crawl_urls(date_start, date_end, limit)
        logger.info(f"Found {len(articles)} articles to enrich.")
        enriched_articles = []
        for article in articles:
            url = article.url
            try:
                results = await crawler.arun(url, config=config)

                for result in results:
                    if result.success:
                        logger.info(f"Successfully crawled {result.url}")

                        content = result.markdown.fit_markdown
                        article.content = content
                        article.status = ArticleStatus.SCRAPED
                        article.crawled_at = datetime.now(timezone.utc)
                        article.scraped_at = datetime.now(timezone.utc)
                        enriched_articles.append(article)
                    else:
                        logger.warning(
                            f"Failed to crawl {result.url}: "
                            f"{result.error_message}"
                        )
            except Exception as e:
                logger.error(f"Error crawling article: {e}")

        await crawler.close()

        return enriched_articles


if __name__ == "__main__":
    # Example usage
    subscription_id = uuid.uuid4()
    subscription = Subscription(
        id=subscription_id,
        name="Handelsblatt Subscription",
        paywall=True,
        domain="https://id.handelsblatt.com/login",
        login_config={
            "container_selector": "[id^='sp_message_container_']",
            "cookies_button": "//button[@title='Zustimmen und weiter' and "
            "contains(@class, 'sp_choice_type_11')]",
            "iframe": "//iframe[contains(@id, 'sp_message_iframe')]",
            "user_input": "form hmg-text-input:nth-of-type(1) input",
            "password_input": "form hmg-text-input:nth-of-type(2) input",
            "submit_button": "form hmg-button > button",
        },
        crawlers={
            "HandelsblattCrawler": {
                "filter_category": True,
                "sourceUri": "handelsblatt.com",
            }
        },
    )
    subscription.username = "your_username"
    subscription.secrets = "your_password"
    crawler = HandelsblattCrawler(
        subscription=subscription,
        sourceUri="handelsblatt.com",
    )

    articles = asyncio.run(
        crawler.crawl_urls(
            date_start=datetime(2025, 7, 1, tzinfo=timezone.utc),
            date_end=datetime(2025, 7, 12, tzinfo=timezone.utc),
            limit=10,
        )
    )
