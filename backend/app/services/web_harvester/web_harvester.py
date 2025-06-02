import asyncio
import random
import time
from typing import Any, List

from sqlmodel import Session
from app.repositories.subscription_repository import SubscriptionRepository
from app.core.logger import get_logger
from app.core.db import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.web_harvester.login import hardcoded_login
from newsplease import NewsPlease
from selenium.webdriver.chrome.options import Options

from app.services.web_harvester.url_extractor import NewsAPIUrlExtractor, UrlExtractor
from app.models.article import Article
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from newsplease.crawler.simple_crawler import SimpleCrawler


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
            logger.error(
                "Subscription or article is None, cannot save article.")
            return
        try:
            await SubscriptionRepository.save_article(self.session, subscription, article)
            logger.info(
                f"Article '{article.title}' saved successfully under subscription '{subscription.name}'.")
        except IntegrityError as e:
            self.session.rollback()
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
        #print(articles_grouped_by_subscription)
        # Each subscription gets their own batch of articles
        for subscription_id, subscription_name, paywall, config, articles in (
            (d['subscription_id'], d['subscription_name'], d['paywall'], d['config'], d['content'])
            for d in articles_grouped_by_subscription
        ):
            if paywall:
            # Handle paywall articles in parallel (with rate limiting)
                print("ping ping2")
            
                #task = self._scrape_paywall_articles(subscription_id, subscription_name, config, articles)
            else:
                print("ping ping ")
                # Handle non-paywalled articles in parallel
                task = asyncio.create_task(
                    self._scrape_regular_articles(subscription_id, subscription_name, articles)
                )
                
                tasks.append(task)

        # Execute all subscription groups concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
                # Log results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing subscription: {result}")
            else:
                logger.info(f"Processed subscription: {result}")
                
    async def _scrape_regular_articles(self, subscription_id: int, subscription_name: str, articles: List[Any]) -> dict:
        """
        Scrape non-paywalled articles.
        """
        logger.info(f"Scraping {len(articles)} regular articles for {subscription_name}")
        
        for article in articles:
            logger.info(f"Scraping article with empty content: {article['url']}")
            try:
                raw_article = NewsPlease.from_url(article["url"])
                article = Article(
                    id=article["article_id"],
                    content=raw_article.maintext,
                    author=raw_article.authors,
                    language=raw_article.language,
                    subscription_id=subscription_id
                )
                
                await SubscriptionRepository.update_article(self.session, article)
                time.sleep(20)
            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to scrape article {article['url']}: {e}")
        
        
        
        

    async def handle_paywall_articles(self, config, subscription_name):
        """
        Handle articles that are paywalled.
        """
        chrome_options = Options()

        chrome_options.add_extension('./cookie-blocker.crx')

        logger.info(f"Trying login for {subscription_name}.")
        driver = webdriver.Chrome(options=chrome_options)

        wait = WebDriverWait(driver, 5)
        newspaper = hardcoded_login(driver, wait, key)



if __name__ == "__main__":


    with Session(engine) as session:
        harvester = WebHarvester(session)
        print("test")
        a = asyncio.run(harvester.scrape_articles())
        print(a)
