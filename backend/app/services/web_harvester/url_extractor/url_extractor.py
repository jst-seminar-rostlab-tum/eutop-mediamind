from abc import ABC, abstractmethod
from typing import List
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
    
if __name__ == "__main__":
    extractor = NewsAPIUrlExtractor()
    urls = extractor.extract_article_urls(
        news_url="bild.de",
        limit=10,
        date_start="2025-05-01",
        date_end="2025-05-31"
    )
    print(urls)  # This will print the extracted article URLs.