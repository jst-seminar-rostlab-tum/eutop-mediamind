import sys
import asyncio

import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from datetime import date

from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.web_harvester.crawl4ai_scraper import process_urls
from app.services.web_harvester.crawler import NewsAPICrawler
# from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import configs
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 初始化 async engine 和 session factory
async_engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI), echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def main():

    crawler = NewsAPICrawler()

    start_date = date(2025, 6, 1)
    end_date = date(2025, 6, 9)

    subscription_id_ft = "b40dc507-537d-4a9f-b423-b8b4fea85740"

    async with AsyncSessionLocal() as session:
        subscription = await SubscriptionRepository.get_subscription_by_id(
            session=session, subscription_id=subscription_id_ft
        )

        articles = crawler.crawl_urls(
            subscription=subscription,
            date_start=start_date,
            date_end=end_date,
            limit=100,
        )
        urls = [article.url for article in articles]
        scraped_results = await process_urls(urls)

        # 更新 content 字段
        for article, result in zip(articles, scraped_results):
            if result.success:
                article.content = result.markdown.fit_markdown
                await SubscriptionRepository.save_article(session, subscription, article)
                print(f"Added: {article.title}")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)