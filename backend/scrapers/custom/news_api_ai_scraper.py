import logging
from typing import Iterator, Any, Dict, Optional
from datetime import datetime

from eventregistry import EventRegistry, QueryArticlesIter

from backend.config.settings import Settings
from backend.models.article import Article
from backend.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG or INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Ensure DEBUG messages are shown in the console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class NewsApiAiScraper(BaseScraper):
    """
    Scraper for NewsAPI.ai using the official Python SDK (eventregistry).

    Configuration (`config` dict) keys:
      - api_key: NewsAPI.ai API key (optional, falls back to Settings.newsapi_ai_key)
      - query: search keywords (string)
      - from: start date YYYY-MM-DD (optional)
      - to: end date YYYY-MM-DD (optional)
      - sources: list or string of source URIs for filtering (optional)
      - max_items: max articles to fetch (default: 100)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        settings = Settings()
        print(settings.API_KEY_NEWS_API_AI)
        self.api_key: str = config.get("api_key") or settings.API_KEY_NEWS_API_AI
        # Initialize EventRegistry client
        self.er = EventRegistry(apiKey=self.api_key, allowUseOfArchive=False)

    def fetch(self) -> Iterator[Any]:
        """
        Use QueryArticlesIter to fetch raw article dicts.
        """
        query: str = self.config.get("query", "")
        date_start: Optional[str] = self.config.get("from")
        date_end: Optional[str] = self.config.get("to")
        sources = self.config.get("sources")
        max_items: int = self.config.get("max_items", 100)

        q = QueryArticlesIter(
            keywords=query,
            dateStart=date_start,
            dateEnd=date_end,
            sourceUri=sources
        )
        for raw in q.execQuery(self.er, maxItems=max_items):
            logger.debug(
                f"Fetched article structure: { {k: v if k != 'body' else '<<omitted>>' for k, v in raw.items()} }")
            logger.debug(f"Fetched article: {raw}")
            yield raw

    def parse(self, raw: Dict[str, Any]) -> Article:
        """
        Parse an EventRegistry article dict into our Article model.
        """
        # Parse publication date
        return Article(**raw)


"""
config = {
    "api_key": "0dd48ba4-0539-4d0f-9962-894ae442092c",  # Replace with your NewsAPI.ai API key
    "query": "",  # Replace with your desired search keywords
    "from": "2025-05-10",  # Replace with your desired start date (YYYY-MM-DD)
    "to": "2025-05-11",  # Replace with your desired end date (YYYY-MM-DD)
    "sources": ["faz.net"],  # Replace with your desired source URIs
    "max_items": 5  # Replace with your desired maximum number of articles
}


# Execute the scraper with the provided configuration
scraper = NewsAPIAIScraper(config)
logger.info("Starting NewsAPI.ai scraper with config: %s", config)
for i in scraper.run():
    print(i)

"""
