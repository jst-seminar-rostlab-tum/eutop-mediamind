from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

import trafilatura

from app.core.logger import BufferedLogger, get_logger
from app.models.article import Article
from app.models.subscription import Subscription

logger = get_logger(__name__)


class Scraper(ABC):
    """
    Initialize the Scraper.
    This class is an abstract base class for web scrapers.
    """

    def __init__(self, subscription: Subscription):
        scraper_name = self.__class__.__name__
        self.logger = BufferedLogger(f"{subscription.name} - {scraper_name}")
        self.subscription = subscription

    @abstractmethod
    def extract(
        self,
        html: str,
        article: Article,
    ) -> Article:
        """
        Given an Article, extract and return the full content
        of the article (and metadata).
        :param article: An Article object containing the URL to scrape.
        :return: An Article object with the full content
        and metadata extracted.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )

    def update_article(
        self,
        article: Article,
        content: str,
        metadata: dict,
    ) -> Article:
        """
        Update the article with the extracted content and metadata.
        :param article: An Article object to update.
        :param content: The extracted content of the article.
        :param metadata: The metadata extracted from the article.
        :return: An updated Article object.
        """
        if not article.title and metadata.get("title"):
            article.title = metadata.get("title")
        if not article.published_at and metadata.get("date"):
            article.published_at = metadata.get("date")
        if not article.authors and metadata.get("author"):
            authors = metadata.get("author").split(";")
            article.authors = authors
        if not article.image_url and metadata.get("image"):
            article.image_url = metadata.get("image")
        if not article.content:
            article.content = content
        article.scraped_at = datetime.now()
        article.status = article.status.SCRAPED
        self.logger.info(
            f"Successfully extracted content for article: {article.url}"
        )
        return article


class TrafilaturaScraper(Scraper):

    def __init__(
        self, subscription: Subscription, trafilatura_kwargs: dict = {}
    ):
        """
        Initialize the TrafilaturaScraper.
        :param subscription: The subscription object containing the source URI.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(subscription)
        self.trafilatura_kwargs = trafilatura_kwargs

        default_trafilatura_kwargs = {
            "output_format": "markdown",
            "include_tables": False,
            "prune_xpath": "//h1 | //title",
            "include_comments": False,
        }

        # If user provides prune_xpath, append it to the default with "|"
        if "prune_xpath" in self.trafilatura_kwargs:
            default_prune = default_trafilatura_kwargs["prune_xpath"]
            specific_prune = self.trafilatura_kwargs["prune_xpath"]
            combined_prune = f"{default_prune} | {specific_prune}"
            default_trafilatura_kwargs["prune_xpath"] = combined_prune
            del self.trafilatura_kwargs["prune_xpath"]

        default_trafilatura_kwargs.update(self.trafilatura_kwargs)
        self.trafilatura_kwargs = default_trafilatura_kwargs

    def extract(
        self,
        html: str,
        article: Article,
    ) -> Article:
        """
        Extracts the full content of an html using Trafilatura.
        :param article: An Article object containing the URL to scrape.
        :return: An Article object with the full content
        and metadata extracted.
        """
        markdown = trafilatura.extract(html, **self.trafilatura_kwargs)

        metadata = trafilatura.extract_metadata(html).as_dict()

        if metadata and markdown:
            self.update_article(article, markdown, metadata)
        else:
            self.logger.error(
                f"Failed to extract content for article: {article.url}"
            )
            article.status = article.status.ERROR
            article.scraped_at = datetime.now()

        return article


class ScraperType(Enum):
    TrafilaturaScraper = "TrafilaturaScraper"


SCRAPER_CLASS_REGISTRY = {
    ScraperType.TrafilaturaScraper: TrafilaturaScraper,
}


def get_scraper(subscription: Subscription):
    for class_name, config in subscription.scrapers.items():
        try:
            crawler_type = ScraperType(class_name)
        except ValueError:
            logger.error(f"Unknown crawler: {class_name}")
            raise ValueError(f"Unknown crawler: {class_name}")
        cls = SCRAPER_CLASS_REGISTRY.get(crawler_type)
        if cls:
            return cls(subscription=subscription, **config)
        else:
            logger.error(f"Unknown crawler: {class_name}")
            raise ValueError(f"Unknown crawler: {class_name}")
