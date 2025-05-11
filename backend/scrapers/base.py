import logging
from abc import ABC, abstractmethod
from typing import Iterator, Any

from backend.models.article import Article

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.

    Each scraper must implement the `fetch` and `parse` methods.
    The `run()` method orchestrates fetching raw data and parsing into Article models.
    """

    def __init__(self, config: dict):
        """
        Initialize scraper with the given configuration.

        Args:
            config (dict): Configuration including credentials, endpoints, and other parameters.
        """
        self.config = config

    @abstractmethod
    def fetch(self) -> Iterator[Any]:
        """
        Fetch raw data from the source.

        Yields:
            Raw response items (e.g., JSON dicts, HTML strings).
        """
        ...

    @abstractmethod
    def parse(self, raw: Any) -> Article:
        """
        Parse raw data into an Article object.

        Args:
            raw (Any): Raw data item returned by `fetch()`.

        Returns:
            Article: Parsed article model.
        """
        ...

    def run(self) -> Iterator[Article]:
        """
        Execute the scraping process: fetch raw items and parse them.

        Yields:
            Article objects ready for further processing.
        """
        for raw in self.fetch():
            try:
                article = self.parse(raw)
                yield article
            except Exception as e:
                logger.exception(f"Failed to parse item: {e}")
                continue