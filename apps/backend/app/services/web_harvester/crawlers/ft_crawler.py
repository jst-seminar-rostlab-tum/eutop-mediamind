import asyncio
import random
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


class FtCrawler(NewsAPICrawler):
    IFRAME_SELECTOR = "[id^='sp_message_iframe_']"
    COOKIE_BUTTON_SELECTOR = "button[title='Accept Cookies']"

    # Login selectors
    SIGNIN_SELECTOR = "#o-header-top-link-signin"
    MY_ACCOUNT_SELECTOR = "#o-header-top-link-myaccount"
    EMAIL_INPUT_SELECTOR = "#enter-email"
    EMAIL_NEXT_SELECTOR = "#enter-email-next"
    PASSWORD_INPUT_SELECTOR = "#enter-password"
    REMEMBER_ME_SELECTOR = "#rememberMe"
    SIGNIN_BUTTON_SELECTOR = "#sign-in-button"

    def __init__(self, subscription: Subscription, sourceUri: str, **kwargs):
        super().__init__(
            subscription=subscription, sourceUri=sourceUri, **kwargs
        )
        self.email = subscription.username
        self.password = subscription.secrets

    async def _check_login_status(self, page: Page) -> bool:
        """Check if user is already logged in."""
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)

            my_account = await page.query_selector(self.MY_ACCOUNT_SELECTOR)
            if my_account:
                return True

            signin = await page.query_selector(self.SIGNIN_SELECTOR)
            if signin:
                return False

            logger.warning("Cannot determine login status")
            return False

        except Exception as e:
            logger.warning(f"Error checking login status: {e}")
            return False

    async def human_click(self, page: Page, selector: str):
        """Simulate human-like click on an element."""
        locator = page.locator(selector).first
        await locator.wait_for(state="visible")
        await locator.scroll_into_view_if_needed()

        box = await locator.bounding_box()
        if not box:
            raise Exception("Element bounding box not found")

        x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
        y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)

        await page.mouse.move(
            x + random.uniform(-30, 30),
            y + random.uniform(-30, 30),
            steps=random.randint(10, 20),
        )
        await asyncio.sleep(random.uniform(0.3, 0.6))
        await page.mouse.move(x, y, steps=random.randint(3, 6))
        await asyncio.sleep(random.uniform(0.2, 0.5))
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.3, 0.7))
        await page.mouse.up()

    async def _perform_login(self, page: Page) -> bool:
        """Perform login process."""
        if not self.email or not self.password:
            logger.error("Email or password not provided for login")
            return False

        try:
            await page.hover(self.SIGNIN_SELECTOR)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await self.human_click(page, self.SIGNIN_SELECTOR)
            await page.wait_for_url("**/login**", timeout=10000)
            await page.wait_for_selector(
                self.EMAIL_INPUT_SELECTOR, timeout=10000
            )
            await self.human_click(page, self.EMAIL_INPUT_SELECTOR)
            await asyncio.sleep(random.uniform(0.5, 1.0))

            for char in self.email:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            await self.human_click(page, self.EMAIL_NEXT_SELECTOR)

            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await page.wait_for_selector(
                self.PASSWORD_INPUT_SELECTOR, timeout=10000
            )
            await self.human_click(page, self.PASSWORD_INPUT_SELECTOR)
            await asyncio.sleep(random.uniform(0.5, 1.0))

            for char in self.password:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))

            # Check remember me
            try:
                remember_checkbox = await page.query_selector(
                    self.REMEMBER_ME_SELECTOR
                )
                if (
                    remember_checkbox
                    and not await remember_checkbox.is_checked()
                ):
                    await page.hover(self.REMEMBER_ME_SELECTOR)
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    await page.check(self.REMEMBER_ME_SELECTOR)
            except Exception as e:
                logger.warning(f"Could not check remember me: {e}")

            await page.locator(self.SIGNIN_BUTTON_SELECTOR).click(
                timeout=10000
            )
            await page.wait_for_timeout(5000)
            await page.screenshot(path="sannysoft_result.png", full_page=True)
            await page.wait_for_selector(
                self.MY_ACCOUNT_SELECTOR, timeout=10000
            )

            return True

        except Exception as e:
            logger.warning(f"Login failed: {e}")
            return False

    async def _handle_login_with_cookies(
        self, page: Page, context: BrowserContext, url: str, **kwargs
    ):
        """Handle both cookie consent and login in sequence."""
        try:
            await asyncio.sleep(random.uniform(2, 5))
            await page.wait_for_selector(self.IFRAME_SELECTOR, timeout=10000)

            iframe_element = await page.query_selector(self.IFRAME_SELECTOR)
            if iframe_element:
                frame = await iframe_element.content_frame()
                if frame:
                    await frame.wait_for_selector(
                        self.COOKIE_BUTTON_SELECTOR, timeout=8000
                    )
                    await frame.hover(self.COOKIE_BUTTON_SELECTOR)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await frame.click(self.COOKIE_BUTTON_SELECTOR)
                else:
                    logger.warning("Unable to access iframe content frame")
            else:
                logger.warning("Cookie consent iframe not found")

        except Exception as e:
            logger.warning(f"Cookie consent handling failed: {e}")

        is_logged_in = await self._check_login_status(page)

        if not is_logged_in:
            logger.info("User not logged in, attempting login")

            login_success = await self._perform_login(page)
            if not login_success:
                logger.warning("Login failed")

        return page

    def _setup_crawler_config(self) -> tuple:
        """Setup crawler configuration."""
        prune_filter = PruningContentFilter(
            threshold=0.8, threshold_type="dynamic", min_word_threshold=10
        )

        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

        browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            use_persistent_context=True,
            user_data_dir=".browser_data",
            extra_args=[
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 "
                "Safari/537.36"
            ],
            viewport_height=900,
            viewport_width=1440,
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
        # Ensure login before main crawling
        login_success = await self._ensure_login()
        if not login_success:
            logger.warning("Failed to ensure login, aborting crawling")
            return []
        browser_config, config = self._setup_crawler_config()
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.start()
        articles = await asyncio.get_event_loop().run_in_executor(
            None, super().crawl_urls, date_start, date_end, limit
        )
        enriched_articles = []
        for article in articles:
            url = article.url
            try:
                results = await crawler.arun(url, config=config)

                for result in results:
                    if result.success:
                        logger.info(f"Successfully crawled {result.url}")

                        content = result.markdown.fit_markdown
                        content = content.replace(
                            "*[FT]: Financial Times", ""
                        ).strip()
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
                logger.warning(f"Error crawling article: {e}")

        await crawler.close()
        return enriched_articles

    async def _ensure_login(self) -> bool:
        """Ensure user is logged in before main crawling."""
        browser_config, config = self._setup_crawler_config()
        crawler = AsyncWebCrawler(config=browser_config)

        try:
            await crawler.start()
            url = "https://www.ft.com/"

            async def login_and_cookie_wrapper(*args, **kwargs):
                return await self._handle_login_with_cookies(*args, **kwargs)

            crawler.crawler_strategy.set_hook(
                "after_goto", login_and_cookie_wrapper
            )

            results = await crawler.arun(url, config=config)
            await crawler.close()

            if results and len(results) > 0:
                return True
            else:
                logger.warning("Login check failed")
                return False

        except Exception as e:
            logger.warning(f"Error during login check: {e}")
            try:
                await crawler.close()
            except Exception:
                pass
            return False


if __name__ == "__main__":
    s = Subscription(
        id=uuid.uuid4(),
        name="Financial Times - Onlinezugang / ePaper",
        paywall=True,
        domain="https://www.ft.com/todaysnewspaper",
        is_active=True,
    )

    s.username = "changethis"
    s.secrets = "changethis"
    crawler = FtCrawler(subscription=s, sourceUri="ft.com")

    articles = asyncio.run(
        crawler.crawl_urls(
            date_start=datetime(2025, 6, 28, tzinfo=timezone.utc),
            date_end=datetime(2025, 6, 30, tzinfo=timezone.utc),
            limit=10,
        )
    )
