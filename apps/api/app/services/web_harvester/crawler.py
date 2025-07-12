from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, List
from urllib.parse import urlparse

import feedparser
import requests
from eventregistry import (
    ArticleInfoFlags,
    EventRegistry,
    QueryArticlesIter,
    ReturnInfo,
)

from app.core.config import configs
from app.core.logger import BufferedLogger, get_logger
from app.models.article import Article
from app.models.subscription import Subscription

logger = get_logger(__name__)


class Crawler(ABC):
    """
    Abstract base class for web crawlers.
    """

    def __init__(self, subscription: Subscription):
        crawler_name = self.__class__.__name__
        self.logger = BufferedLogger(f"{subscription.name} - {crawler_name}")
        self.subscription = subscription

    @abstractmethod
    def crawl_urls(
        self,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        limit: int = -1,
    ) -> List[Article]:
        """
        Given a Subscription, extract and returns a list of Articles
          (with the urls and subscription id at minimum).

        :param date_start: The start date for the crawl (optional).
        :param date_end: The end date for the crawl (optional).
        :param limit: The maximum number of articles to retrieve (default is
        -1, which means no limit).
        :return: A list of URLs pointing to individual news articles.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )


class NewsAPICrawler(Crawler):
    """
    A crawler that uses the NewsAPI.ai service to extract article URLs
    based on a subscription.
    This crawler fetches articles from the NewsAPI.ai database
    based on the subscription's sourceURI.
    """

    def __init__(
        self,
        subscription: Subscription,
        sourceUri: str,
        include_blogs: bool = False,
        filter_category: bool = True,
    ):
        super().__init__(subscription)

        if not configs.NEWSAPIAI_API_KEY:
            self.logger.error(
                "NEWSAPIAI_API_KEY is not set in the configuration."
            )
            raise ValueError(
                "NEWSAPIAI_API_KEY is not set in the configuration."
            )

        try:
            self.er = EventRegistry(apiKey=configs.NEWSAPIAI_API_KEY)
        except Exception as e:
            self.logger.error(f"Failed to initialize EventRegistry: {e}")
            raise

        self.logger.info("NewsAPICrawler initialized with API key.")

        self.sourceUri = sourceUri
        self.include_blogs = include_blogs
        self.filter_category = filter_category

    def crawl_urls(
        self,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        limit: int = -1,
    ) -> List[Article]:

        query = self._build_query(date_start, date_end)

        articles_query_iter = QueryArticlesIter.initWithComplexQuery(query)

        returnInfo = ReturnInfo(
            articleInfo=ArticleInfoFlags(
                categories=True, authors=True, image=True
            )
        )

        articles = []
        for article in articles_query_iter.execQuery(
            self.er, maxItems=limit, sortBy="rel", returnInfo=returnInfo
        ):
            category_list = (
                [
                    category.get("uri")
                    for category in article.get("categories", [])
                ]
                if article.get("categories")
                else []
            )

            author_list = (
                [author.get("name") for author in article.get("authors", [])]
                if article.get("authors")
                else []
            )

            published_at_str = article.get("dateTimePub")
            published_at = None
            if published_at_str:
                try:
                    published_at = datetime.strptime(
                        published_at_str, "%Y-%m-%dT%H:%M:%SZ"
                    )
                except ValueError:
                    self.logger.warning(
                        f"Could not parse dateTimePub: {published_at_str}"
                    )

            articles.append(
                Article(
                    title=article.get("title"),
                    url=article.get("url"),
                    published_at=published_at,
                    authors=author_list,
                    subscription_id=self.subscription.id,
                    categories=category_list,
                    relevance=article.get("relevance", 0),
                    image_url=article.get("image"),
                    language=self._parse_language(article.get("lang")),
                )
            )

        self.logger.info(
            f"Found {len(articles)} for {self.subscription.name}."
        )
        if not articles:
            self.logger.info(
                f"No articles found for {self.subscription.name}."
            )
            return []

        return articles

    def _build_query(
        self, date_start: datetime | None, date_end: datetime | None
    ):
        """
        Builds the query for the EventRegistry API.
        """
        query_conditions = [
            {"sourceUri": self.sourceUri},
        ]

        if self.filter_category:
            query_conditions.append(
                {
                    "$or": [
                        {"categoryUri": "news/Business"},
                        {"categoryUri": "news/Environment"},
                        {"categoryUri": "news/Health"},
                        {"categoryUri": "news/Politics"},
                        {"categoryUri": "news/Science"},
                        {"categoryUri": "news/Technology"},
                    ]
                }
            )

        if date_start and date_end:
            query_conditions.append(
                {
                    "dateStart": date_start.strftime("%Y-%m-%d"),
                    "dateEnd": date_end.strftime("%Y-%m-%d"),
                }
            )

        datatypes = ["news"]
        if self.include_blogs:
            datatypes.append("blog")

        return {
            "$query": {"$and": query_conditions},
            "$filter": {
                "dataType": datatypes,
                "isDuplicate": "skipDuplicates",
            },
        }

    def _parse_language(self, language: str) -> str | None:
        """
        Parses the language code from the article and returns a standardized
        two-letter language code.
        """
        lang_map = {"deu": "de", "eng": "en", "fra": "fr"}
        if not language:
            return None
        return lang_map.get(language, language.upper())

    def get_best_matching_source(self, prefix: str) -> Any | None:
        """
        Checks if a domain is included in the NewsAPI.ai database
        and returns the best match.

        Parameters:
            prefix (str): The URL to check.

        Returns:
            dict: The source with the highest relevance score,
              or None if no suitable source is found.
        """
        # Extract the domain from the URL
        parsed_url = urlparse(prefix)
        domain = parsed_url.netloc

        # Define the API endpoint and parameters
        url = "https://newsapi.ai/api/v1/suggestSources"
        params = {"prefix": domain, "apiKey": configs.NEWSAPIAI_API_KEY}

        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise error for bad status codes

            # Parse the JSON response
            sources = response.json()

            if not sources:
                self.logger.info("No sources found for the given prefix.")
                return None

            # Find the source with the highest score
            best_source = max(sources, key=lambda x: x.get("score", 0))

            # Check if the score is above the threshold
            if best_source.get("score", 0) >= 50000:
                return best_source
            else:
                self.logger.info(
                    "Found source has a score below 50,000. Ignoring."
                )
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"An error occurred during the API request: {e}")
            return None

    def __str__(self):
        return (
            f"NewsAPICrawler(subscription={self.subscription.name}, "
            "sourceUri={self.sourceUri})"
        )


class RSSFeedCrawler(Crawler):
    """
    A crawler that uses RSS feeds to extract article URLs
    based on a subscription.
    This crawler fetches articles from the RSS feed of the source URI.
    This crawler should be scheduled to run periodically
    to keep the articles up-to-date.
    """

    def __init__(
        self, subscription: Subscription, feed_urls: List[str], language: str
    ):
        super().__init__(subscription)
        self.feed_urls = feed_urls
        self.language = language

    def crawl_urls(
        self,
        date_start: datetime | None = None,
        date_end: datetime | None = None,
        limit: int = -1,
    ) -> List[Article]:
        articles: List[Article] = []

        for feed_url in self.feed_urls:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if limit != -1 and len(articles) >= limit:
                    break

                published = None
                if "published_parsed" in entry and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif "updated_parsed" in entry and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    # If no date, skip
                    continue

                # Filter by date range if specified
                if date_start and published < date_start:
                    continue
                if date_end and published > date_end:
                    continue

                # Extract authors (if any)
                authors = []
                if "authors" in entry:
                    authors = [
                        author.name
                        for author in entry.authors
                        if hasattr(author, "name")
                    ]
                elif "author" in entry:
                    authors = [entry.author]

                # Extract categories/tags (if any)
                categories = []
                if "tags" in entry:
                    categories = [
                        tag.term for tag in entry.tags if hasattr(tag, "term")
                    ]

                article = Article(
                    title=entry.title,
                    url=entry.link,
                    authors=authors if authors else None,
                    published_at=published,
                    language=self.language,
                    categories=categories if categories else None,
                    subscription_id=self.subscription.id,
                )
                articles.append(article)

            if limit != -1 and len(articles) >= limit:
                break
        return articles


class CrawlerType(Enum):
    NewsAPICrawler = "NewsAPICrawler"
    RSSFeedCrawler = "RSSFeedCrawler"
    FtCrawler = "FtCrawler"
    HandelsblattCrawler = "HandelsblattCrawler"


def _get_crawler_class(crawler_type: CrawlerType):
    """Lazy import crawler classes to avoid circular imports."""
    if crawler_type == CrawlerType.NewsAPICrawler:
        return NewsAPICrawler
    elif crawler_type == CrawlerType.RSSFeedCrawler:
        return RSSFeedCrawler
    elif crawler_type == CrawlerType.HandelsblattCrawler:
        from app.services.web_harvester.crawlers.handelsblatt_crawler import (
            HandelsblattCrawler,
        )

        return HandelsblattCrawler
    elif crawler_type == CrawlerType.FtCrawler:
        from app.services.web_harvester.crawlers.ft_crawler import FtCrawler

        return FtCrawler
    else:
        raise ValueError(f"Unknown crawler type: {crawler_type}")


def get_crawlers(subscription: Subscription):
    crawlers = {}
    for class_name, config in subscription.crawlers.items():
        try:
            crawler_type = CrawlerType(class_name)
        except ValueError:
            logger.error(f"Unknown crawler: {class_name}")
            raise ValueError(f"Unknown crawler: {class_name}")

        cls = _get_crawler_class(crawler_type)
        if cls:
            crawlers[class_name] = cls(subscription=subscription, **config)
        else:
            logger.error(f"Unknown crawler: {class_name}")
            raise ValueError(f"Unknown crawler: {class_name}")
    return crawlers
