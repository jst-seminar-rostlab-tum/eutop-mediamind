import asyncio
import re
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
from app.models.article import Article
from app.models.subscription import Subscription
from app.services.web_harvester.crawler import Crawler
from app.services.web_harvester.scraper import TrafilaturaScraper

logger = get_logger(__name__)

# List to store matched articles
matched_articles = []

# Set to keep track of already seen URLs to avoid duplicates
_seen_urls = set()

# Unique session ID for the crawler
session_id = str(uuid.uuid4())

# Regex pattern to match URLs from Enhesa
URL_PATTERN = re.compile(r"^https://product\.enhesa\.com/\d+$")
hook_info = {"newly_matched": 0, "early_article": False}


# Hook：automatically extract links from the page
async def extract_enhesa_links(
    page: Page, date_start: datetime, date_end: datetime, **kwargs
):
    unfilterd_articles = await page.eval_on_selector_all(
        "div.innerContainer",
        """nodes => nodes.map(node => {
        const anchor = node.querySelector("a[href^='/']");
        const dateDiv = node.querySelector("div.smallText");
        const href = anchor?.getAttribute("href") || null;
        const date = dateDiv?.innerText.trim() || null;
        if (!href || !/\\/\\d+$/.test(href)) return null;

        return {
            url: "https://product.enhesa.com" + href,
            date: date
        };
    }).filter(Boolean)""",
    )
    newly_matched = 0
    early_article_found = False
    for art in unfilterd_articles:
        try:
            clean = re.sub(r"\s+", " ", art["date"]).strip()
            parsed_date = datetime.strptime(clean, "%d %B %Y").replace(
                tzinfo=timezone.utc
            )
            if parsed_date < date_start:
                early_article_found = True
            if (
                date_start <= parsed_date <= date_end
                and art["url"] not in _seen_urls
            ):
                matched_articles.append({"url": art["url"], "date": clean})
                _seen_urls.add(art["url"])
                newly_matched += 1
        except Exception as e:
            logger.warning(f"Failed to parse {repr(art['date'])}: {e}")
    return newly_matched, early_article_found


class EnhesaCrawler(Crawler):

    def __init__(
        self,
        subscription: Subscription,
    ):
        super().__init__(
            subscription=subscription,
        )
        self.loged_in = False
        self.tScraper = TrafilaturaScraper(
            subscription=subscription,
        )

    def _setup_crawler_config(self):
        prune_filter = PruningContentFilter(
            threshold=0.45, threshold_type="dynamic", min_word_threshold=5
        )
        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
        browser_config = BrowserConfig(
            headless=True,
            verbose=True,
        )
        config = CrawlerRunConfig(
            markdown_generator=md_generator,
            wait_until="networkidle",
            session_id=session_id,
            scan_full_page=True,
        )

        return browser_config, config

    async def _perform_login(self, page: Page, login_config: dict):
        if not self.loged_in:
            try:
                logger.info("Starting login process...")

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
                logger.info("Login process completed")
                self.loged_in = True
                return True

            except Exception as e:
                logger.error(f"Login failed: {e}")
                return False

    async def _crawl_single_page(
        self, crawler: AsyncWebCrawler, page_num: int, config: CrawlerRunConfig
    ) -> tuple[List[Article], bool]:
        """Crawl a single page and return Article objects
        and whether to stop."""
        url = f"https://product.enhesa.com/news-insight?page={page_num}"

        try:
            await crawler.arun(url, config=config)
            page_articles = []
            has_out_of_range_article = False
            return page_articles, has_out_of_range_article

        except Exception as e:
            logger.error(f"Error crawling page {page_num}: {e}")
            return [], False

    async def crawl_urls(
        self,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        limit: int = -1,
    ) -> List[Article]:
        browser_config, config = self._setup_crawler_config()
        crawler = AsyncWebCrawler(config=browser_config)

        async def login_wrapper(
            page: Page, context: BrowserContext, url: str = None, **kwargs
        ):
            if not self.loged_in:
                await self._perform_login(page, self.subscription.login_config)
            return page

        crawler.crawler_strategy.set_hook("after_goto", login_wrapper)

        async def before_retrieve_html_hook(page: Page, **kwargs):
            newly_matched, early_article = await extract_enhesa_links(
                page, date_start=date_start, date_end=date_end
            )
            hook_info["newly_matched"] = newly_matched
            hook_info["early_article"] = early_article

        crawler.crawler_strategy.set_hook(
            "before_retrieve_html", before_retrieve_html_hook
        )

        await crawler.start()

        all_articles: List[Article] = []
        page_num = 0
        max_pages = 1000
        should_stop = False

        while page_num <= max_pages and not should_stop:
            await self._crawl_single_page(crawler, page_num, config)
            if hook_info["early_article"] and hook_info["newly_matched"] == 0:
                should_stop = True
            if limit > 0 and len(all_articles) >= limit:
                should_stop = True

            page_num += 1

        final_articles = []
        for article_url in matched_articles:
            sub_result = await crawler.arun(
                article_url["url"],
                config=config,
            )
            if sub_result.success:
                article = Article(
                    url=article_url["url"],
                    published_at=datetime.strptime(
                        article_url["date"], "%d %B %Y"
                    ).replace(tzinfo=timezone.utc),
                )
                final_articles.append(
                    self.tScraper.extract(sub_result.html, article)
                )

        await crawler.close()

        return final_articles


if __name__ == "__main__":
    # Example usage
    subscription_id = uuid.uuid4()
    subscription = Subscription(
        id=subscription_id,
        name="Chemical Watch - Onlinezugang",
        paywall=True,
        domain="https://product.enhesa.com/",
        login_config={
            "user_input": "input[name='email']",
            "password_input": "input[name='password']",
            "submit_button": "button[data-testid='login-button']",
            "logout_button": "div.hoverable >> text=Log out",
        },
        crawlers={
            "EnhesaCrawler": {
                "filter_category": True,
                "sourceUri": "https://www.product.enhesa.com",
            }
        },
    )
    subscription.username = "change_this"
    subscription.secrets = "change_this"
    crawler = EnhesaCrawler(
        subscription=subscription,
    )

    articles = asyncio.run(
        crawler.crawl_urls(
            date_start=datetime(2025, 7, 10, tzinfo=timezone.utc),
            date_end=datetime(2025, 7, 10, tzinfo=timezone.utc),
            limit=10,
        )
    )
