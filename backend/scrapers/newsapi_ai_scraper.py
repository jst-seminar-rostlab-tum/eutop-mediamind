import logging
from typing import Iterator, Any, Dict, Optional
from datetime import datetime

from eventregistry import EventRegistry, QueryArticlesIter



from base import BaseScraper

logger = logging.getLogger(__name__)

class NewsAPIAIScraper(BaseScraper):
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
        self.api_key: str = config.get("api_key") or settings.newsapi_ai_key
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
            yield raw

    def parse(self, raw: Dict[str, Any]) -> Article:
        """
        Parse an EventRegistry article dict into our Article model.
        """
        # Parse publication date
        date_iso: Optional[str] = raw.get("datePublishedIso")
        published_dt: Optional[datetime] = None
        if date_iso:
            try:
                published_dt = datetime.fromisoformat(date_iso)
            except ValueError:
                logger.warning("Invalid ISO date format: %s", date_iso)

        # Extract source name
        source_info = raw.get("source", {})
        source_name = source_info.get("title") if isinstance(source_info, dict) else None

        return Article(
            title=raw.get("title", "").strip(),
            author=raw.get("author"),
            published_at=published_dt,
            source=source_name,
            url=raw.get("url"),
            text=raw.get("body") or "",
            keywords=[self.config.get("query")] if self.config.get("query") else [],
            entities=raw.get("entities", [])
        )

    



from newsapi_ai_client import NewsApiAiClient

config = {
    "api_key": "",  # Replace with your NewsAPI.ai API key
    "query": "",  # Replace with your desired search keywords
    "from": "2025-05-10",  # Replace with your desired start date (YYYY-MM-DD)
    "to": "2023-05-11",  # Replace with your desired end date (YYYY-MM-DD)
    "sources": ["faz.net"],  # Replace with your desired source URIs
    "max_items": 5  # Replace with your desired maximum number of articles
}


# Execute the scraper with the provided configuration
scraper = NewsAPIAIScraper(config)
result = scraper.run()

print(result)

