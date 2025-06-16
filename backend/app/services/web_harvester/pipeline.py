import asyncio
from datetime import date

from app.repositories.article_repository import ArticleRepository
import time
from app.repositories.subscription_repository import (
    get_subscriptions_with_crawlers,
)

if __name__ == "__main__":
    """with Session(sync_engine) as session:
    horizont = SubscriptionRepository.get_subscription_by_id(
        session=session,
        subscription_id="bf210331-e2e7-4912-8eca-c3276d44ff15",
    )
    a = SeparateCrawlerScraper(
        session=session,
        crawler=NewsAPICrawler(),
        scraper=TrafilaturaScraper(),
    ).crawl_and_scrape(subscription=horizont, skip_crawling=True)
    print(a)"""

    async def main():  # Just testing the pipeline, will remove later
        a = await get_subscriptions_with_crawlers()
        for subscription in a:
            c = subscription.crawlers["NewsAPICrawler"]
            articles = c.crawl_urls(
                date_start=date.today(),
                date_end=date.today(),
                limit=100,
            )
            c.logger.flush()
            start_time = time.time()

            try:
                await ArticleRepository.create_articles_batch(articles)
            except Exception as e:
                continue
            elapsed_time = time.time() - start_time
            print(f"Storing all articles took {elapsed_time:.2f} seconds")

    if __name__ == "__main__":
        asyncio.run(main())
