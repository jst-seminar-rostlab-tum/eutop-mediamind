import asyncio
import random
import time

from sqlmodel import Session
from app.repositories.subscription_repository import SubscriptionRepository
from app.core.logger import get_logger
from app.core.db import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from newsplease import NewsPlease

from app.services.web_harvester.url_extractor import NewsAPIUrlExtractor, UrlExtractor
from app.models.article import Article

from sqlalchemy.exc import IntegrityError

logger = get_logger(__name__)

class WebHarvester:
    def __init__(self, session: AsyncSession, urlextractor: UrlExtractor = NewsAPIUrlExtractor()):
        self.session = session
        self.urlextractor = urlextractor

    async def fetch_subscriptions(self):
        subscriptions = await SubscriptionRepository.get_all_no_paywall_with_newsapi_id(self.session)
        return subscriptions
    
    async def save_article(self, subscription, article):
        """
        Save an article to the database under the given subscription.
        """
        if not subscription or not article:
            logger.error("Subscription or article is None, cannot save article.")
            return
        try:
            await SubscriptionRepository.save_article(self.session, subscription, article)
            logger.info(f"Article '{article.title}' saved successfully under subscription '{subscription.name}'.")
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Article '{article.title}' already exists under subscription '{subscription.name}'")
        except Exception as e:
            logger.error(f"Failed to save article '{article.title}': {e}")
    
    async def fetch_articles(self):
        subscriptions = await self.fetch_subscriptions()
        for subscription in subscriptions:
            logger.info(f"Processing subscription: {subscription.name}")
            articles = self.urlextractor.extract_article_urls(subscription=subscription, limit=200)
            if articles:
                logger.info(f"Found {len(articles)} articles for subscription: {subscription.name}")
            else:
                logger.warning(f"No articles found for subscription: {subscription.name}")
            for article in articles:
                await self.save_article(subscription, article)
    
    async def scrape_articles_with_empty_content(self):
        """
        Scrape articles that have empty content and save them.
        """
        articles = await SubscriptionRepository.get_articles_with_empty_content(self.session)
        if not articles:
            logger.info("No articles with empty content found.")
            return
        
        for article_id, url, paywall, subscription_id in articles:
            if paywall:
                logger.info(f"Skipping paywalled article: {url}")
                continue
            else:
                logger.info(f"Scraping article with empty content: {url}")
                try:
                    raw_article = NewsPlease.from_url(url)
                    article = Article(
                        id=article_id,
                        content=raw_article.maintext,
                        author=raw_article.authors,
                        language=raw_article.language,
                        subscription_id=subscription_id
                    )
                    await SubscriptionRepository.update_article(self.session, article)
                    logger.info(f"Article {url} scraped and updated successfully.")
                    time.sleep(random.uniform(2, 4))  
                except Exception as e:
                    logger.error(f"Failed to scrape article {url}: {e}")
                    continue
                    

        
    # async def run(self):
    #     """
    #     Run the harvester to fetch and save articles.
    #     """
    #     try:
    #         await self.fetch_articles()
    #         logger.info("Fetching and saving articles completed")
            
            
            
    #     except Exception as e:
    #         logger.error(f"Web harvester encountered an error: {e}")
    #         raise e

if __name__ == "__main__":
    with Session(engine) as session:
        harvester = WebHarvester(session)
        asyncio.run(harvester.scrape_articles_with_empty_content())
        
    

    