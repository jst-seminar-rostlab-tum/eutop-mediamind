import asyncio
from newsplease import NewsPlease
from newspaper import Article
from sqlmodel import Session
from app.core.db import engine
from app.repositories.subscription_repository import SubscriptionRepository


if __name__ == "__main__":
    from newsplease.crawler.simple_crawler import SimpleCrawler
    with Session(engine) as session:
        a = asyncio.run(SubscriptionRepository.get_articles_with_empty_content(session))
        print(a[0])
        print(a[1])
        print(a[2])

