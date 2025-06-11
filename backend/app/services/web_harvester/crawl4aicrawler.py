import sys
import asyncio

import asyncio
import sys
from uuid import UUID

from datetime import date
from app.models.article import ArticleStatus
from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.web_harvester.crawl4ai_scraper import process_urls
from app.services.web_harvester.crawler import NewsAPICrawler
# from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import configs
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime

# 初始化 async engine 和 session factory
async_engine = create_async_engine(str(configs.SQLALCHEMY_DATABASE_URI), echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def main():

    crawler = NewsAPICrawler()

    start_date = date(2025, 5, 15)
    end_date = date(2025, 5, 31)

    subscription_id = UUID("b316d770-455d-4d90-80e4-4911b1850c0e")

    async with AsyncSessionLocal() as session:
        stmt = select(Subscription).where(Subscription.newsapi_id.isnot(None)).limit(1)
        result = await session.execute(stmt)
        subscription = result.scalars().first()
        subscription = await SubscriptionRepository.get_subscription_by_id(
            session, subscription_id
        )

        # Add this check
        if not subscription:
            print(f"Error: Subscription with ID {subscription_id} not found")
            return


        articles = crawler.crawl_urls(
            subscription=subscription,
            date_start=start_date,
            date_end=end_date,
            limit=1000,
        )
        urls = [article.url for article in articles]
        scraped_results = await process_urls(urls)

        
        for article, result in zip(articles, scraped_results):
            if result.success:
                article.content = result.markdown.fit_markdown
                article.status = ArticleStatus.SCRAPED
                article.scraped_at = datetime.now()
                await SubscriptionRepository.save_article(session, subscription_id, article)
                print(f"Added: {article.title}")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)