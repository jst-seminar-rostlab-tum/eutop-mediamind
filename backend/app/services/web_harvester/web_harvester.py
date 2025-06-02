import asyncio
import random
import time

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

    async def scrape_articles_with_empty_content(self):
        """
        Scrape articles that have empty content and save them.
        """
        articles = await SubscriptionRepository.get_articles_with_empty_content(self.session)
        if not articles:
            logger.info("No articles with empty content found.")
            return

        for article_id, url, paywall, config, subscription_id, subscription_name in articles:
            if paywall:
                logger.info(f"Skipping paywalled article: {url}")
                context = self.handle_paywall_articles(
                    config, subscription_name)
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
                    logger.info(
                        f"Article {url} scraped and updated successfully.")
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.error(f"Failed to scrape article {url}: {e}")
                    continue

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

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1200,800")
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--start-fullscreen")  # Optional
    # <<< Keeps Chrome open after script ends
    chrome_options.add_experimental_option("detach", True)

    chrome_options.add_extension(
        './app/services/web_harvester/utils/cookie-blocker.crx')
    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(driver, 5)
    newspaper = hardcoded_login(driver, wait, "SZ - ePaper + Onlinezugang", paper={
        "login_button": "//a[contains(@href, 'auth.sueddeutsche.de') and contains(text(), 'Anmelden')]",
        "user_input": "//input[@id='login' and @name='email']",
        "password_input": "//input[@id='current-password' and @name='current-password']",
        "submit_button": "//button[@type='submit' and contains(text(), 'Einloggen')]",
        "logout_button": "//a[contains(@href, '/abmelden')]"
    })
    if newspaper:
        driver.get(
            "https://www.welt.de/regionales/hessen/article256176216/nach-sechs-jahren-ebbe-fraport-macht-hoffnung-auf-dividende.html")
        html = driver.page_source

        # Save to local file
        with open("sueddeutsche_article.html", "w", encoding="utf-8") as f:
            f.write(html)
        a = NewsPlease.from_html(
            driver.page_source)
        print(a.maintext)
        print(a.title)

    """ with Session(engine) as session:
        harvester = WebHarvester(session)
        a = asyncio.run(harvester.fetch_articles())
        print(len(a)) """
