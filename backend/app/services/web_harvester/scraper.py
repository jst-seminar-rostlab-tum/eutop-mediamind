import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import trafilatura

from app.core.logger import get_logger
from app.models.article import Article

logger = get_logger(__name__)


class Scraper(ABC):
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


class TrafilaturaScraper(Scraper):
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
        html_data = trafilatura.extract(
            html, output_format="json", with_metadata=True
        )

        if html_data:
            html_data = json.loads(html_data)
            if not article.title:
                article.title = html_data.get("title")
            if not article.published_at:
                article.published_at = html_data.get("date")
            if not article.author:
                article.author = html_data.get("authors")
            if not article.content:
                article.content = html_data.get("raw_text")
            article.scraped_at = datetime.now()
            article.status = article.status.SCRAPED
        else:
            logger.error(
                f"Failed to extract content for article: {article.url}"
            )
            article.status = article.status.ERROR
            article.scraped_at = datetime.now()

        return article
