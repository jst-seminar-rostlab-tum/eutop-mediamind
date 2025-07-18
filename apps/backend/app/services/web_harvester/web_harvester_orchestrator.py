import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from selenium.webdriver.support.ui import WebDriverWait

from app.core.logger import get_logger
from app.models.article import Article, ArticleStatus
from app.models.crawl_stats import CrawlStats
from app.models.subscription import Subscription
from app.repositories.article_repository import ArticleRepository
from app.repositories.crawl_stats_repository import CrawlStatsRepository
from app.repositories.subscription_repository import (
    get_subscriptions_with_crawlers,
    get_subscriptions_with_scrapers,
)
from app.services.article_cleaner.article_valid_check import (
    clean_article_llm,
    is_article_valid,
)
from app.services.web_harvester.crawler import Crawler, CrawlerType
from app.services.web_harvester.scraper import Scraper
from app.services.web_harvester.utils.web_utils import (
    create_driver,
    get_response_code,
    hardcoded_login,
    hardcoded_logout,
    safe_execute_script,
    safe_page_load,
)

logger = get_logger(__name__)


async def run_crawler(
    crawler: CrawlerType,
    date_start: datetime = datetime.combine(date.today(), datetime.min.time()),
    date_end: datetime = datetime.now(),
    limit: int = 100,
):
    subscriptions = await get_subscriptions_with_crawlers(crawler)

    async def run_crawler_runner(subscription, crawler):
        crawler: Crawler = subscription.crawlers[crawler.value]
        crawl_result = crawler.crawl_urls(
            date_start=date_start,
            date_end=date_end,
            limit=limit,
        )

        # Check if crawl_urls returned a coroutine (async method)
        import inspect

        if inspect.iscoroutine(crawl_result):
            articles = await crawl_result
        else:
            articles = crawl_result

        await ArticleRepository.create_articles_batch(
            articles, logger=crawler.logger
        )
        crawler.logger.flush()

    await asyncio.gather(
        *(run_crawler_runner(sub, crawler) for sub in subscriptions)
    )


async def run_scraper():
    subscriptions = await get_subscriptions_with_scrapers()
    executor = ThreadPoolExecutor(max_workers=3)

    try:
        tasks = [
            _scrape_articles_for_subscription(sub, executor)
            for sub in subscriptions
        ]
        await asyncio.gather(*tasks)
    finally:
        executor.shutdown(wait=True)


async def _scrape_articles_for_subscription(subscription, executor):
    """
    Seperated selenium code to run in a thread pool executor. Selenium is not
    designed to be run in an async context, so we use a thread pool to run it
    in a separate thread.
    Async Context is used to interact with the database
    """
    scraper: Scraper = subscription.scrapers
    new_articles = await ArticleRepository.list_new_articles_by_subscription(
        subscription_id=subscription.id
    )

    loop = asyncio.get_event_loop()
    scraped_articles = await loop.run_in_executor(
        executor, run_selenium_code, new_articles, subscription, scraper, loop
    )

    logger.info(f"Scraper executor done for Subscription {subscription.name}.")
    # Store every scraped article in the database
    for article in scraped_articles:

        if (
            article.status != ArticleStatus.ERROR
            and article.content is not None
        ):
            if not is_article_valid(article.content):
                cleaned_content = await clean_article_llm(article.content)
                if cleaned_content.strip() == "":
                    article.note = (
                        "Article doesn't look like a news article "
                        "after cleaning."
                    )
                    article.status = ArticleStatus.ERROR
                else:
                    article.content = cleaned_content
        await ArticleRepository.update_article(article)

    logger.info(f"Inserted all articles for Subscription {subscription.name}.")
    # Log the crawler stats
    successful_articles = [
        article
        for article in scraped_articles
        if article.status == ArticleStatus.SCRAPED
    ]
    distinct_notes = set(
        article.note for article in scraped_articles if article.note
    )
    joined_notes = "; ".join(distinct_notes)
    crawl_stats = CrawlStats(
        subscription_id=subscription.id,
        total_attempted=len(scraped_articles),
        total_successful=len(successful_articles),
        notes=joined_notes,
    )
    await CrawlStatsRepository.insert_crawl_stats(crawl_stats)

    scraper.logger.info(
        f"Finished scraping {len(scraped_articles)} articles for subscription"
        f" {subscription.name}."
    )
    scraper.logger.flush()


def run_selenium_code(
    articles: list[Article], subscription: Subscription, scraper: Scraper, loop
) -> list[Article]:
    scraper: Scraper = subscription.scrapers
    driver, wait = create_driver(headless=True)
    login_success = False
    try:
        login_success = _handle_login_if_needed(
            subscription, scraper, driver, wait
        )
        if subscription.paywall and not login_success:
            scraper.logger.info(
                f"Login failed for subscription {subscription.name}, "
                f"updating login config with LLM approach"
            )
            # Disabled because the scheduler should take care of this
            # login_updated_future = asyncio.run_coroutine_threadsafe(
            #     LoginLLM.add_page(subscription), loop
            # )
            # subscription_updated = login_updated_future.result()
            # if subscription_updated:
            #     scraper.logger.info(
            #         f"Login config updated for {subscription.name}, "
            #         f"retrying login"
            #     )
            #     login_success = _handle_login_if_needed(
            #         subscription_updated, scraper, driver, wait
            #     )
            # else:
            #     scraper.logger.error(
            #         f"Could not update login config for subscription "
            #         f"{subscription.name} with LLM approach."
            #     )

        if subscription.paywall and not login_success:
            scraper.logger.error(
                f"Login failed for subscription {subscription.name}. "
                "Skipping scraping."
            )
            return _scraper_error_handling(articles, "Login failed")

        scraper.logger.info(
            f"Starting scraping for {len(articles)} articles from subscription"
            f" {subscription.name}..."
        )
        scraped_articles = _scrape_articles(scraper, driver, articles)
        return scraped_articles
    except Exception as e:
        scraper.logger.error(
            f"Error during scraping for subscription {subscription.name}: {e}"
        )
        return _scraper_error_handling(articles, str(e))
    finally:
        _handle_logout_and_cleanup(
            driver, wait, subscription, scraper, login_success
        )


def _handle_login_if_needed(subscription, scraper, driver, wait) -> bool:
    if subscription.paywall:
        login_success = hardcoded_login(driver, wait, subscription)
        time.sleep(2)
        if login_success:
            scraper.logger.info(f"Login successful for {subscription.name}")
        else:
            scraper.logger.error(
                f"Login failed for {subscription.name}. Skipping scraping."
            )
        return login_success
    else:
        scraper.logger.info(
            f"Subscription {subscription.name} does not require login."
        )
        return True


def _scrape_articles(scraper, driver, new_articles):
    scraped_articles = []
    for idx, article in enumerate(new_articles):
        try:
            if idx % 10 == 0:
                scraper.logger.info(
                    f"Scraping article {idx + 1}/{len(new_articles)}"
                )
                scraper.logger.flush()
            # Load the page with frame detachment handling
            try:
                # Use safe page loading to handle frame detachment
                if not safe_page_load(driver, article.url):
                    raise ValueError(f"Failed to load page: {article.url}")

                # Wait for page to be fully loaded with safe script execution
                WebDriverWait(driver, 30).until(
                    lambda d: safe_execute_script(
                        d, "return document.readyState"
                    )
                    == "complete"
                )
            except Exception as load_error:
                error_msg = str(load_error)
                if "target frame detached" in error_msg.lower():
                    raise ValueError(
                        f"Frame detached loading {article.url}: {load_error}"
                    )
                else:
                    raise ValueError(
                        f"Timeout loading page {article.url}: {load_error}"
                    )

            # Check response code of the main page
            response_code = get_response_code(driver, article.url)
            if response_code >= 300:
                raise ValueError(
                    f"Received HTTP {response_code} for {article.url}"
                )

            # Scrape the article content
            html = driver.page_source
            scraped_article = scraper.extract(html=html, article=article)
            scraped_articles.append(scraped_article)
            scraper.logger.info(
                f"Scraped article: {scraped_article.title} with content "
                f"{scraped_article.content[:100]}..."
            )
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            scraper.logger.error(f"Error scraping article {article.url}: {e}")
            article.status = ArticleStatus.ERROR
            article.note = str(e)
            scraped_articles.append(article)
            continue
    return scraped_articles


def _handle_logout_and_cleanup(
    driver, wait, subscription, scraper, login_success
):
    try:
        if login_success and subscription.paywall:
            try:
                hardcoded_logout(
                    driver=driver, wait=wait, subscription=subscription
                )
            except Exception as e:
                scraper.logger.error(
                    f"Error logging out for subscription "
                    f"{subscription.name}: {e}"
                )
    finally:
        try:
            driver.quit()
            logger.info(f"{subscription.name} Driver quit successfully.")
        except Exception as e:
            scraper.logger.error(f"Error quitting driver: {e}")


def _scraper_error_handling(articles: list[Article], error: str):
    for article in articles:
        article.status = ArticleStatus.ERROR
        article.note = error
    return articles
