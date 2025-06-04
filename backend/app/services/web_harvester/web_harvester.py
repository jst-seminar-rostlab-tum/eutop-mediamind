import asyncio
import random
import time
from typing import Any, List

from sqlmodel import Session
from app.repositories.subscription_repository import SubscriptionRepository
from app.core.logger import get_logger
from app.core.db import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.web_harvester.login import hardcoded_login
from newsplease import NewsPlease
from selenium.webdriver.chrome.options import Options

from app.services.web_harvester.url_extractor import NewsAPIUrlExtractor, UrlExtractor
from app.models.article import Article
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from newsplease.crawler.simple_crawler import SimpleCrawler
from sqlalchemy.ext.asyncio import create_async_engine
import logging

from sqlalchemy.exc import IntegrityError

logger = get_logger(__name__)


logging.getLogger("newsplease").setLevel(logging.CRITICAL)



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
            logger.error(
                "Subscription or article is None, cannot save article.")
            return
        try:
            await SubscriptionRepository.save_article(self.session, subscription, article)
            logger.info(
                f"Article '{article.title}' saved successfully under subscription '{subscription.name}'.")
        except IntegrityError as e:
            await self.session.rollback()  # Use await for async sessions
            logger.warning(
                f"Article '{article.title}' already exists under subscription '{subscription.name}'")
        except Exception as e:
            logger.error(f"Failed to save article '{article.title}': {e}")

    async def fetch_articles(self):
        subscriptions = await self.fetch_subscriptions()
        for subscription in subscriptions:
            logger.info(f"Processing subscription: {subscription.name}")
            articles = self.urlextractor.extract_article_urls(
                subscription=subscription, limit=100)
            if articles:
                logger.info(
                    f"Found {len(articles)} articles for subscription: {subscription.name}")
            else:
                logger.warning(
                    f"No articles found for subscription: {subscription.name}")
            for article in articles:
                await self.save_article(subscription, article)

    async def scrape_articles(self):
        """
        Scrape articles that have empty content and save them.
        """
        articles_grouped_by_subscription = await SubscriptionRepository.get_articles_with_empty_content(self.session)
        
        if not articles_grouped_by_subscription:
            logger.info("No articles with empty content found.")
            return
        
        await self._start_scraping(articles_grouped_by_subscription)

    async def _start_scraping(self, articles_grouped_by_subscription):
        tasks = []
        
        # Each subscription gets their own batch of articles
        for subscription_id, subscription_name, subscription_domain, paywall, config, articles in (
            (d['subscription_id'], d['subscription_name'], d['domain'], d['paywall'], d['config'], d['content'])
            for d in articles_grouped_by_subscription
        ):
            if paywall:
                task = asyncio.create_task(
                    self._scrape_paywall_articles(subscription_id, subscription_name, subscription_domain, articles, config)
                )
                tasks.append(task)
            else:
                # Handle non-paywalled articles in parallel
                task = asyncio.create_task(
                    self._scrape_regular_articles(subscription_id, subscription_name, articles)
                )
                tasks.append(task)

        # Execute all subscription groups concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error during scraping: {result}")
                else:
                    logger.info(f"Scraping result: {result}")
            
    async def _scrape_regular_articles(self, subscription_id: int, subscription_name: str, articles: List[Any]) -> dict:
        """
        Scrape non-paywalled articles sequentially within each subscription.
        """
        logger.info(f"Scraping {len(articles)} regular articles for {subscription_name}")
        
        successes = 0
        failures = 0
        
        # Process articles sequentially within this subscription
        for article_data in articles:
            try:
                html = await SimpleCrawler.crawl(article_data["url"])
                success = await self._scrape_single_article(subscription_id, article_data, html)
                if success:
                    successes += 1
                else:
                    failures += 1
                    
            except Exception as e:
                failures += 1
                logger.error(f"Failed to scrape article {article_data['url']}: {e}")
        
        logger.info(f"Completed scraping for {subscription_name}: {successes} successes, {failures} failures")
        
        return {
            'subscription_name': subscription_name,
            'successes': successes,
            'failures': failures
        }
                
    async def _scrape_single_article(self, subscription_id: int, article_data: dict, html) -> bool:
        """
        Scrape a single article with proper async handling.
        """
        try:
            logger.info(f"Scraping article with empty content: {article_data['url']}")
            raw_article = NewsPlease.from_html(html)
            
            article = Article(
                id=article_data["article_id"],
                content=raw_article.maintext,
                author=", ".join(raw_article.authors) if raw_article.authors else None,
                language=raw_article.language,
                subscription_id=subscription_id
            )
            engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/mediamind")
            async_session = async_sessionmaker(engine, class_=AsyncSession)
            # Create a new session for this operation to avoid conflicts
            async with async_session() as article_session:
                await SubscriptionRepository.update_article(article_session, article)
            await asyncio.sleep(10)  # Adjust delay as needed
            return True
            
        except Exception as e:
            logger.error(f"Failed to scrape article {article_data['url']}: {e}")
            raise e

    async def _scrape_paywall_articles(self, subscription_id, subscription_name, subscription_domain, articles, config):
        """
        Handle articles that are paywalled.
        """
        logger.info(f"Scraping {len(articles)} paywalled articles for {subscription_name}")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_extension('./app/services/web_harvester/utils/cookie-blocker.crx')
       

        logger.info(f"Trying login for {subscription_name}.")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 5)
        login_success = hardcoded_login(driver, wait, subscription_name, config, subscription_domain)  
        if login_success:
            logger.info(f"Login successful for {subscription_name}.")
            for article_data in articles:
                driver.get(article_data["url"])
                html = driver.page_source
                await self._scrape_single_article(subscription_id, article_data, html)
        else:
            logger.error(f"Login failed for {subscription_name}.")
            driver.quit()
            return
        
        
        


# Example usage with proper async session
async def main():
    # Create async session
    
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/mediamind")
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        harvester = WebHarvester(session)
        print("Starting article scraping...")
        await harvester.scrape_articles()
        print("Article scraping completed.")


if __name__ == "__main__":
    asyncio.run(main())