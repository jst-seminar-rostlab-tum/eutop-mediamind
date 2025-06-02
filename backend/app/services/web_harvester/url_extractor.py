from abc import ABC, abstractmethod
from typing import Any, List
from urllib.parse import urlparse

import requests
from eventregistry import EventRegistry, QueryArticlesIter
from app.core.logger import get_logger
from app.core.config import configs
from app.models.article import Article
from app.models.subscription import Subscription

logger = get_logger(__name__)


class UrlExtractor(ABC):
    @abstractmethod
    def extract_article_urls(
        self,
        subscription: Subscription,
        limit: int = 50,
        date_start: str = None,
        date_end: str = None
    ) -> List[Article]:
        """
        Given a Subscription, extract and returns a list of Articles,
        optionally filtered by a date range. If no date range is provided,
        it returns the most recent articles up to the specified limit.

        :param news_url: A list of news URLs to extract article links from.
        :param limit: The maximum number of article URLs to return.
        :param date_start: The start date (inclusive) for filtering articles, in 'YYYY-MM-DD' format.
        :param date_end: The end date (inclusive) for filtering articles, in 'YYYY-MM-DD' format.
        :return: A list of URLs pointing to individual news articles.
        """
        pass


class NewsAPIUrlExtractor(UrlExtractor):
    def __init__(self):
        """
        Initializes the NewsAPIUrlExtractor with the necessary configurations.
        """
        if not configs.NEWSAPIAI_API_KEY:
            raise ValueError("NEWSAPIAI_API_KEY is not set in the configuration.")
        logger.info("NewsAPIUrlExtractor initialized with API key.")
        self.api_key = configs.NEWSAPIAI_API_KEY
    
    def extract_article_urls(
        self,
        subscription: Subscription,
        limit: int = 50,
        date_start: str = None,
        date_end: str = None
    ) -> List[Article]:
        try:
            er = EventRegistry(apiKey=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize EventRegistry: {e}")
            return []

        newsapi_id = subscription.newsapi_id
        if not newsapi_id:
            logger.error(f"{subscription.name} does not have a NewsAPI ID.")
            return []
        
        query_conditions = [
            {"$or": [{"sourceUri": newsapi_id}]},
            {
                "$or": [
                    {"categoryUri": "news/Environment"},
                    {"categoryUri": "news/Business"},
                    {"categoryUri": "news/Health"},
                    {"categoryUri": "news/Politics"},
                    {"categoryUri": "news/Technology"},
                    {"categoryUri": "news/Science"},
                ]
            }
        ]
        
        if date_start and date_end:
            query_conditions.append({"dateStart": date_start, "dateEnd": date_end})

        query = {
            "$query": {
                "$and": query_conditions
            }
        }
        
        q = QueryArticlesIter.initWithComplexQuery(query)

        articles = []
        for article in q.execQuery(er, maxItems=limit):
            articles.append(
            Article(
                title=article.get("title"),
                url=article.get("url"),
                published_at=article.get("dateTime"),
                author=article.get("author", None),
            )
            )

        logger.info(f"Number of articles: {len(articles)}")

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
        url = 'https://newsapi.ai/api/v1/suggestSources'
        params = {
            'prefix': domain,
            'apiKey': self.api_key
        }

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
            best_source = max(sources, key=lambda x: x.get('score', 0))

            # Check if the score is above the threshold
            if best_source.get('score', 0) >= 50000:
                return best_source
            else:
                logger.info("Found source has a score below 50,000. Ignoring.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during the API request: {e}")
            return None


if __name__ == "__main__":
    extractor = NewsAPIUrlExtractor()
    urls = extractor.extract_article_urls(
        subscription=Subscription(
            id="12345",
            name="Example Subscription",
            newsapi_id="topagrar.com"
        ),
        limit=10
    )
    print(urls)  # This will print the extracted article URLs.
