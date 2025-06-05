from abc import ABC, abstractmethod
from time import sleep

from app.models.subscription import Subscription
from app.services.web_harvester.crawler import Crawler
from app.services.web_harvester.scraper import Scraper
from sqlmodel import Session
from app.repositories.article_repository import ArticleRepository
from app.core.logger import get_logger
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from app.services.web_harvester.utils.login import hardcoded_login
from fake_useragent import UserAgent


logger = get_logger(__name__)


class CrawlerScraper(ABC):
    """
    Abstract base class for web crawler scrapers.

    This class defines the interface for an end to end web crawler scraper.
    It combines the functionality of a crawler and a scraper to extract data from web pages.
    """

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def crawl_and_scrape(self, subscription: Subscription, **kwargs) -> dict:
        """
        Crawls the given URL and scrapes data from it.
        :param url: The URL to crawl and scrape.
        :return: A dictionary containing the scraped data.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def save_articles(self, articles: list) -> None:
        """
        Saves the scraped articles to the database.
        :param articles: A list of articles to save.
        """
        return ArticleRepository.insert_articles(articles, self.session)

    def get_articles(self, subscription_id: str) -> list:
        """
        Retrieves articles for a given subscription with empty content.
        :param subscription: A Subscription object to retrieve articles for.
        :return: A list of articles associated with the subscription.
        """
        return ArticleRepository.get_articles_by_subscription_with_empty_content(
            self.session, subscription_id)

    def update_article(self, article) -> None:
        """
        Updates an existing article in the database.
        :param article: An Article object to update.
        """
        return ArticleRepository.update_article(self.session, article)


class SeparateCrawlerScraper(CrawlerScraper):
    """
    A specific implementation of CrawlerScraper that can be used to crawl and scrape data.

    This class can be extended to implement specific crawling and scraping logic.
    """

    def __init__(self, session: Session, crawler: Crawler, scraper: Scraper):
        super().__init__(session)
        self.crawler = crawler
        self.scraper = scraper

    def crawl_and_scrape(self, subscription: Subscription, **kwargs) -> dict:
        """
        Overrides the base method to provide specific crawling and scraping logic.
        :param subscription: A Subscription object containing the URL to crawl and scrape.
        :param skip_crawling: If True, skips the crawling step and retrieves articles directly.
        :param kwargs: Additional keyword arguments that can be used to customize the crawling and scraping process.
        :return: A dictionary containing the scraped data.
        """

        if subscription is None:
            logger.error("Subscription cannot be None")
            raise ValueError("Subscription cannot be None")

        if kwargs.get("skip_crawling", False):
            articles = self.get_articles(subscription.id)
        else:
            # Extract crawler-related kwargs
            crawler_kwargs = {
                key: kwargs.get(key)
                for key in ("date_start", "date_end", "limit")
                if key in kwargs
            }

            articles = self.crawler.crawl_urls(subscription, **crawler_kwargs)
            if not articles:
                logger.info(
                    f"No articles found for subscription {subscription.name}")
                return {}

            articles = self.save_articles(articles)

        scraped_articles = []
        chrome_options = Options()

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(
            "--enable-features=NetworkService,NetworkServiceInProcess")
        # optional but common with headless
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f'--user-agent={UserAgent().random}')

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 5)
        if subscription.paywall:
            login_success = hardcoded_login(
                driver, wait, subscription)
            sleep(5)
            if login_success:
                logger.info(f"Login successful for {subscription.name}")
            else:
                logger.error(
                    f"Login failed for {subscription.name}. Skipping scraping.")
                driver.quit()
                return {}
        else:
            logger.info(
                f"Subscription {subscription.name} does not require login.")
        for article in articles:
            driver.get(article.url)
            html = driver.page_source
            scraped_article = self.scraper.extract(
                html=html,
                article=article
            )
            inserted_article = self.update_article(scraped_article)
            logger.info(
                f"Scraped article: {inserted_article.title} with content {inserted_article.content[:100]}...")
            scraped_articles.append(inserted_article)
            sleep(5)
        return scraped_articles
