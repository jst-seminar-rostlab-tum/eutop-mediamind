import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

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
from app.services.login_llm_service import LoginLLM
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

        await ArticleRepository.create_articles_batch(articles, logger=logger)

    await asyncio.gather(
        *(run_crawler_runner(sub, crawler) for sub in subscriptions)
    )


# Configure timeouts
SELENIUM_TASK_TIMEOUT = 5400  # 90 minutes per subscription
EXECUTOR_SHUTDOWN_TIMEOUT = 30  # 30 seconds to shutdown executor


async def run_scraper():
    subscriptions = await get_subscriptions_with_scrapers()
    executor = ThreadPoolExecutor(max_workers=2)

    try:
        tasks = []
        for sub in subscriptions:
            task = _scrape_articles_for_subscription_with_timeout(
                sub, executor
            )
            tasks.append(task)

        # Use asyncio.gather with return_exceptions=True to handle individual
        # failures
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions that occurred
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(
                    f"Subscription {subscriptions[i].name} failed: {result}"
                )

    finally:
        # Force shutdown executor with timeout
        await _shutdown_executor_safely(executor)


async def _scrape_articles_for_subscription_with_timeout(
    subscription, executor
):
    """Wrapper with timeout for scraping articles"""
    try:
        return await asyncio.wait_for(
            _scrape_articles_for_subscription(subscription, executor),
            timeout=SELENIUM_TASK_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.error(
            f"Timeout scraping subscription {subscription.name} after "
            f"{SELENIUM_TASK_TIMEOUT}s"
        )
        # Return empty list or handle as needed
        return []


async def _scrape_articles_for_subscription(subscription, executor):
    """
    Separated selenium code to run in a thread pool executor. Selenium is not
    designed to be run in an async context, so we use a thread pool to run it
    in a separate thread.
    Async Context is used to interact with the database
    """
    scraper: Scraper = subscription.scrapers
    new_articles = await ArticleRepository.list_new_articles_by_subscription(
        subscription_id=subscription.id
    )

    if not new_articles:
        logger.info(f"No new articles for subscription {subscription.name}")
        return []

    loop = asyncio.get_event_loop()

    try:
        # Add timeout to the executor task
        scraped_articles = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                run_selenium_code_safe,
                new_articles,
                subscription,
                scraper,
                loop
            ),
            timeout=SELENIUM_TASK_TIMEOUT - 10,  # Leave some buffer
        )

        logger.info(
            f"Scraper executor done for Subscription {subscription.name}."
        )

    except asyncio.TimeoutError:
        logger.error(
            f"Selenium task timed out for subscription {subscription.name}"
        )
        # Return articles with error status
        scraped_articles = _scraper_error_handling(
            new_articles, "Selenium task timeout"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error in scraper for {subscription.name}: {e}"
        )
        scraped_articles = _scraper_error_handling(new_articles, str(e))

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
    await _log_crawl_stats(subscription, scraped_articles)

    logger.info(
        f"Finished scraping {len(scraped_articles)} articles for subscription"
        f" {subscription.name}."
    )

    return scraped_articles


def run_selenium_code_safe(
    articles: list[Article], subscription: Subscription, scraper: Scraper, loop
) -> list[Article]:
    """
    Safer version of run_selenium_code with better error handling and cleanup
    """
    driver = None
    wait = None
    login_success = False

    try:
        driver, wait = create_driver(headless=True)
        login_success = _handle_login_if_needed(
            subscription, scraper, driver, wait
        )


        if subscription.paywall and not login_success:
                        now = datetime.now(timezone.utc)
            # One weekly attempt per subscription
            next_attempt = (
                subscription.llm_login_attempt + timedelta(days=7)
                if subscription.llm_login_attempt
                else None
            )
            if subscription.llm_login_attempt is None or now >= next_attempt:
                logger.info(
                    f"Login failed for subscription {subscription.name}, "
                    f"updating login config with LLM approach"
                )
                login_updated_future = asyncio.run_coroutine_threadsafe(
                    LoginLLM.add_page(subscription), loop
                )
                subscription_updated = login_updated_future.result()

                if subscription_updated:
                    logger.info(
                        f"Login config updated for {subscription.name}, "
                        f"retrying login"
                    )
                    login_success = _handle_login_if_needed(
                        subscription_updated, scraper, driver, wait
                    )
                else:
                    logger.warning(
                        f"Could not update login config for subscription "
                        f"{subscription.name} with LLM approach."
                    )

        if subscription.paywall and not login_success:
            logger.warning(
                f"Login failed for subscription {subscription.name}. "
                "Skipping scraping."
            )
            return _scraper_error_handling(articles, "Login failed")

        logger.info(
            f"Starting scraping for {len(articles)} articles from subscription"
            f" {subscription.name}..."
        )

        scraped_articles = _scrape_articles(scraper, driver, articles)
        return scraped_articles

    except Exception as e:
        logger.error(
            f"Error during scraping for subscription {subscription.name}: {e}"
        )
        return _scraper_error_handling(articles, str(e))
    finally:
        # Ensure cleanup always happens
        _cleanup_driver_safe(
            driver, wait, subscription, scraper, login_success
        )


def _cleanup_driver_safe(driver, wait, subscription, scraper, login_success):
    """Safe cleanup with timeout protection"""
    if driver is None:
        return

    try:
        # Logout with timeout protection
        if login_success and subscription.paywall:
            try:
                hardcoded_logout(
                    driver=driver, wait=wait, subscription=subscription
                )
            except Exception as e:
                logger.error(
                    f"Error logging out for subscription "
                    f"{subscription.name}: {e}"
                )
    finally:
        # Force quit driver
        try:
            driver.quit()
            logger.info(f"{subscription.name} Driver quit successfully.")
        except Exception as e:
            logger.warning(f"Error quitting driver: {e}")
            try:
                driver.service.process.terminate()
                logger.info(
                    f"Force terminated driver process for {subscription.name}"
                )
            except Exception as e:
                logger.warning(
                    f"Error force terminating driver" f" process: {e}"
                )


async def _shutdown_executor_safely(executor):
    """Safely shutdown executor with timeout"""
    try:
        # First try graceful shutdown
        executor.shutdown(wait=False)

        # Wait for shutdown with timeout
        loop = asyncio.get_event_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, executor.shutdown, True),
            timeout=EXECUTOR_SHUTDOWN_TIMEOUT,
        )
        logger.info("Executor shutdown successfully")

    except asyncio.TimeoutError:
        logger.warning("Executor shutdown timed out, forcing termination")
        # Force termination of remaining threads
        for thread in executor._threads:
            if thread.is_alive():
                logger.warning(f"Force terminating thread {thread.name}")
                # Note: There's no clean way to force kill threads in Python
                # Might need to use process-based approach if this is a
                # persistent issue
    except Exception as e:
        logger.error(f"Error during executor shutdown: {e}")


async def _log_crawl_stats(subscription, scraped_articles):
    """Extract crawl stats logging to separate function"""
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


def _handle_login_if_needed(subscription, scraper, driver, wait) -> bool:
    if subscription.paywall:
        login_success = hardcoded_login(driver, wait, subscription)
        time.sleep(2)
        if login_success:
            logger.info(f"Login successful for {subscription.name}")
        else:
            logger.warning(
                f"Login failed for {subscription.name}. Skipping scraping."
            )
        return login_success
    else:
        logger.info(
            f"Subscription {subscription.name} does not require login."
        )
        return True


def _scrape_articles(scraper, driver, new_articles):
    scraped_articles = []
    for idx, article in enumerate(new_articles):
        try:
            if idx % 10 == 0:
                logger.info(f"Scraping article {idx + 1}/{len(new_articles)}")

            # Load the page with frame detachment handling
            try:
                if not safe_page_load(driver, article.url):
                    raise ValueError(f"Failed to load page: {article.url}")

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
            logger.info(
                f"Scraped article: {scraped_article.title} with content "
                f"{scraped_article.content[:100]}..."
            )
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.warning(f"Error scraping article {article.url}: {e}")
            article.status = ArticleStatus.ERROR
            article.note = str(e)
            scraped_articles.append(article)
            continue
    return scraped_articles


def _scraper_error_handling(articles: list[Article], error: str):
    for article in articles:
        article.status = ArticleStatus.ERROR
        article.note = error
    return articles
