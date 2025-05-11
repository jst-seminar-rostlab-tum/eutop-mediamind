"""
Factory to instantiate the appropriate Scraper class based on configuration.
"""

import importlib
from typing import Dict, Type

from sqlalchemy.orm import Session

from backend.scrapers.base import BaseScraper

def get_scraper(source_config: Dict, db: Session) -> BaseScraper:
    """
        Return an instance of a scraper based on source_config. source_config must include a 'scraper_type' type: 'newsapi_ai'
        The scraper_key is used to determine which scraper class to instantiate.
    """

    scraper_type = source_config.get("scraper_type")
    if not scraper_type:
        raise ValueError("source_config missing 'scraper_type' field")

    module_name = scraper_type.lower()
    print(module_name)
    class_name = ''.join(part.capitalize() for part in module_name.split('_'))
    print(class_name)
    try:
        module = importlib.import_module(f"backend.scrapers.custom.{module_name}")
        ScraperClass = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Could not find scraper for type '{scraper_type}': {e}")

    return ScraperClass(source_config, db)
