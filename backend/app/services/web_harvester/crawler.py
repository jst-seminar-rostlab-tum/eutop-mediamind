from abc import ABC, abstractmethod
from datetime import date as Date
from typing import Any, List
from urllib.parse import urlparse

import requests
from eventregistry import EventRegistry, QueryArticlesIter

from app.core.config import configs
from app.core.logger import get_logger
from app.models.article import Article
from app.models.subscription import Subscription

logger = get_logger(__name__)


class Crawler(ABC):
    @abstractmethod
    def crawl_urls(
        self,
        subscription: Subscription,
        date_start: Date | None = None,
        date_end: Date | None = None,
        limit: int = -1,
    ) -> List[Article]:
        """
        Given a Subscription, extract and returns a list of Articles (with the urls and subscription id at minimum).

        :param subscription: A Subscription object containing the URL to crawl.
        :return: A list of URLs pointing to individual news articles.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )


class NewsAPICrawler(Crawler):
    """
    A crawler that uses the NewsAPI.ai service to extract article URLs based on a subscription.
    This crawler fetches articles from the NewsAPI.ai database based on the subscription's NewsAPI ID.
    """

    def __init__(self):
        if not configs.NEWSAPIAI_API_KEY:
            raise ValueError(
                "NEWSAPIAI_API_KEY is not set in the configuration."
            )
        self.api_key = configs.NEWSAPIAI_API_KEY
        logger.info("NewsAPICrawler initialized with API key.")

    def crawl_urls(
        self,
        subscription: Subscription,
        date_start: Date | None = None,
        date_end: Date | None = None,
        limit: int = -1,
    ) -> List[Article]:
        try:
            er = EventRegistry(apiKey=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize EventRegistry: {e}")
            return []

        newsapi_id = subscription.newsapi_id
        if not newsapi_id:
            logger.info(f"{subscription.name} does not have a NewsAPI ID.")
            return []

        query_conditions = [
            {"$or": [{"sourceUri": newsapi_id}]},
        ]

        if date_start and date_end:
            query_conditions.append(
                {
                    "dateStart": date_start.strftime("%Y-%m-%d"),
                    "dateEnd": date_end.strftime("%Y-%m-%d"),
                }
            )

        query = {
            "$query": {"$and": query_conditions},
            "$filter": {"dataType": ["news", "blog"]},
            "resultType": "articles",
            "articlesSortBy": "date",
        }

        q = QueryArticlesIter.initWithComplexQuery(query)

        articles = []
        for article in q.execQuery(er, maxItems=limit):
            articles.append(
                Article(
                    title=article.get("title"),
                    url=article.get("url"),
                    published_at=article.get("dateTimePub"),
                    author=article.get("author", None),
                    subscription_id=subscription.id,
                    category_uri=article.get("categoryUri", None),
                )
            )

        logger.info(f"Found {len(articles)} for {subscription.name}.")
        if not articles:
            logger.info(f"No articles found for {subscription.name}.")
            return []

        return articles

    def get_best_matching_source(self, prefix: str) -> Any | None:
        """
        Checks if a domain is included in the NewsAPI.ai database and returns the best match.

        Parameters:
            prefix (str): The URL to check.

        Returns:
            dict: The source with the highest relevance score, or None if no suitable source is found.
        """
        # Extract the domain from the URL
        parsed_url = urlparse(prefix)
        domain = parsed_url.netloc

        # Define the API endpoint and parameters
        url = "https://newsapi.ai/api/v1/suggestSources"
        params = {"prefix": domain, "apiKey": self.api_key}

        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise error for bad status codes

            # Parse the JSON response
            sources = response.json()

            if not sources:
                logger.info("No sources found for the given prefix.")
                return None

            # Find the source with the highest score
            best_source = max(sources, key=lambda x: x.get("score", 0))

            # Check if the score is above the threshold
            if best_source.get("score", 0) >= 50000:
                return best_source
            else:
                logger.info("Found source has a score below 50,000. Ignoring.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during the API request: {e}")
            return None
