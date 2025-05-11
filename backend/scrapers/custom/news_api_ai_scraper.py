import logging
from typing import Iterator, Any, Dict, Optional
from datetime import datetime, timedelta, date

from eventregistry import EventRegistry, QueryArticlesIter
from sqlalchemy.orm import Session

from backend.config.settings import Settings
from backend.models.article import Article, Source, Author
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

    def __init__(self, config: Dict[str, Any], db: Session) -> None:
        super().__init__(config)
        self.db = db
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

        if date_start is None and date_end is None:
            today = date.today()
            yesterday = today - timedelta(days=1)
            date_start = yesterday.isoformat()  # YYYY-MM-DD
            date_end = today.isoformat()

        sources = self.config.get("url")
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
        Parse an EventRegistry article dict into unser Article-Model.
        CamelCase in snake_case mappen und vorhandene Source wiederverwenden.
        """
        # 1) Mappe die einfachen Felder
        mapped = {
            "uri":           raw.get("uri"),
            "lang":          raw.get("lang"),
            "is_duplicate":  raw.get("isDuplicate"),
            "date":          date.fromisoformat(raw.get("date")),
            "time":          raw.get("time"),
            "date_time":     datetime.fromisoformat(raw.get("dateTime").replace("Z", "+00:00")),
            "date_time_pub": datetime.fromisoformat(raw.get("dateTimePub").replace("Z", "+00:00")),
            "data_type":     raw.get("dataType"),
            "sim":           raw.get("sim", 0.0),
            "url":           raw.get("url"),
            "title":         raw.get("title"),
            "body":          raw.get("body"),
            "image":         raw.get("image"),
            "event_uri":     raw.get("eventUri"),
            "sentiment":     raw.get("sentiment"),
            "wgt":           raw.get("wgt"),
            "relevance":     raw.get("relevance"),
        }

        # 2) Article nur mit den gemappten Feldern anlegen
        article = Article(**mapped)

        # 3) Source: get-or-create basierend auf uri
        src_data = raw.get("source", {})
        src_uri = src_data.get("uri")
        if src_uri:
            # vorausgesetzt, self.db ist eure SQLAlchemy-Session
            existing = self.db.query(Source).filter_by(uri=src_uri).first()
            if existing:
                article.source = existing
            else:
                article.source = Source(
                    uri=src_uri,
                    data_type=src_data.get("dataType"),
                    title=src_data.get("title"),
                )

        # 4) Authors anlegen und anhängen
        for a in raw.get("authors", []):
            article.authors.append(
                Author(
                    uri=a.get("uri"),
                    is_agency=a.get("isAgency", False)
                )
            )

        return article

