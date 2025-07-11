import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from app.models.article import Article, ArticleStatus
from app.models.crawl_stats import CrawlStats
from app.models.subscription import Subscription
from app.repositories.article_repository import ArticleRepository
from app.repositories.crawl_stats_repository import CrawlStatsRepository
from app.repositories.subscription_repository import (
    get_subscriptions_with_crawlers,
    get_subscriptions_with_scrapers,
)
from app.services.web_harvester.crawler import Crawler, CrawlerType
from app.services.web_harvester.scraper import Scraper
from app.services.web_harvester.utils.web_utils import (
    create_driver,
    get_response_code,
    hardcoded_login,
    hardcoded_logout,
)


async def run_crawler(
    crawler: CrawlerType,
    date_start: datetime = datetime.combine(date.today(), datetime.min.time()),
    date_end: datetime = datetime.now(),
    limit: int = 100,
):
    subscriptions = await get_subscriptions_with_crawlers(crawler)

    async def run_crawler_runner(subscription, crawler):
        crawler: Crawler = subscription.crawlers[crawler.value]
        articles = crawler.crawl_urls(
            date_start=date_start,
            date_end=date_end,
            limit=limit,
        )
        await ArticleRepository.create_articles_batch(
            articles, logger=crawler.logger
        )
        crawler.logger.flush()

    await asyncio.gather(
        *(run_crawler_runner(sub, crawler) for sub in subscriptions)
    )


async def run_scraper():
    subscriptions = await get_subscriptions_with_scrapers()
    executor = ThreadPoolExecutor(max_workers=2)

    tasks = [
        _scrape_articles_for_subscription(sub, executor)
        for sub in subscriptions
    ]
    await asyncio.gather(*tasks)


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
        executor, run_selenium_code, new_articles, subscription, scraper
    )

    # Store every scraped article in the database
    for article in scraped_articles:
        await ArticleRepository.update_article(article)

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
    articles: list[Article], subscription: Subscription, scraper: Scraper
) -> list[Article]:
    scraper: Scraper = subscription.scrapers
    driver, wait = create_driver(headless=True)
    login_success = False
    try:
        login_success = _handle_login_if_needed(
            subscription, scraper, driver, wait
        )
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
        if login_success:
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
            driver.get(article.url)

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
    if login_success and subscription.paywall:
        try:
            hardcoded_logout(
                driver=driver, wait=wait, subscription=subscription
            )
        except Exception as e:
            scraper.logger.error(
                f"Error logging out for subscription {subscription.name}: {e}",
            )
    driver.quit()


def _scraper_error_handling(articles: list[Article], error: str):
    for article in articles:
        article.status = ArticleStatus.ERROR
        article.note = error
    return articles


if __name__ == "__main__":
    # Example usage
    asyncio.run(
        run_crawler(
            CrawlerType.RSSFeedCrawler,
            date_start=datetime(2025, 1, 1),
            date_end=datetime(2025, 12, 31),
            limit=-1,
        )
    )
