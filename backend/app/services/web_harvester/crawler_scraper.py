from abc import ABC, abstractmethod

from app.models.subscription import Subscription
from app.services.web_harvester.crawler import Crawler
from app.services.web_harvester.scraper import Scraper


class CrawlerScraper(ABC):
    """
    Abstract base class for web crawler scrapers.

    This class defines the interface for an end to end web crawler scraper.
    It combines the functionality of a crawler and a scraper to extract data from web pages.
    """
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def crawl_and_scrape(self, subscription: Subscription) -> dict:
        """
        Crawls the given URL and scrapes data from it.
        :param url: The URL to crawl and scrape.
        :return: A dictionary containing the scraped data.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    

class SeparateCrawlerScraper(CrawlerScraper):
    """
    A specific implementation of CrawlerScraper that can be used to crawl and scrape data.
    
    This class can be extended to implement specific crawling and scraping logic.
    """
    def __init__(self, crawler: Crawler, scraper: Scraper):
        super().__init__()
        self.crawler = crawler
        self.scraper = scraper

    def crawl_and_scrape(self, subscription: Subscription) -> dict:
        """
        Overrides the base method to provide specific crawling and scraping logic.
        :param subscription: A Subscription object containing the URL to crawl and scrape.
        :return: A dictionary containing the scraped data.
        """
        articles = self.crawler.crawl_urls(subscription)
        scraped_articles = []

        for article in articles:
            scraped_article = self.scraper.extract(article)
            scraped_articles.append(scraped_article)

        return scraped_articles
