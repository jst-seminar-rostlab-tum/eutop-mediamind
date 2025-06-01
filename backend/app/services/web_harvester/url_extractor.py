from abc import ABC, abstractmethod
from typing import Any, List
from urllib.parse import urlparse

import requests
from eventregistry import EventRegistry, QueryArticlesIter
from app.core.logger import get_logger
from app.core.config import configs

logger = get_logger(__name__)


class UrlExtractor(ABC):
    @abstractmethod
    def extract_article_urls(
        self,
        news_url: str,
        limit: int = 50,
        date_start: str = None,
        date_end: str = None
    ) -> List[str]:
        """
        Given a list of news URLs, extract and return a list of sub-URLs that are news articles,
        optionally filtered by a date range.

        :param news_url: A list of news URLs to extract article links from.
        :param limit: The maximum number of article URLs to return.
        :param date_start: The start date (inclusive) for filtering articles, in 'YYYY-MM-DD' format.
        :param date_end: The end date (inclusive) for filtering articles, in 'YYYY-MM-DD' format.
        :return: A list of URLs pointing to individual news articles.
        """
        pass


class NewsAPIUrlExtractor(UrlExtractor):
    def extract_article_urls(
        self,
        news_url: str,
        limit: int = 50,
        date_start: str = None,
        date_end: str = None
    ) -> List[str]:
        try:
            er = EventRegistry(apiKey=configs.NEWSAPIAI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize EventRegistry: {e}")
            return []

        query = {
            "$query": {
                "$and": [
                    {"$or": [{"sourceUri": news_url}]},
                    {
                        "$or": [
                            {"categoryUri": "news/Environment"},
                            {"categoryUri": "news/Business"},
                            {"categoryUri": "news/Health"},
                            {"categoryUri": "news/Politics"},
                            {"categoryUri": "news/Technology"},
                            {"categoryUri": "news/Science"},
                        ]
                    },
                    {"dateStart": date_start, "dateEnd": date_end},
                ]
            }
        }

        q = QueryArticlesIter.initWithComplexQuery(query)

        articles = []
        for article in q.execQuery(er, maxItems=limit):
            articles.append(
                {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "datetime": article.get("dateTime"),
                    "author": article.get("author", None),
                }
            )

        logger.info(f"Number of articles: {len(articles)}")
        for a in articles:
            logger.debug(f"{a['title']} {a['url']}")

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
            'apiKey': configs.NEWSAPIAI_API_KEY
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
    urls = extractor.get_best_matching_source(
        "https://www.tagesschau.de/ukraine/ukraine-krieg-100.html"
    )
    print(urls)  # This will print the extracted article URLs.
