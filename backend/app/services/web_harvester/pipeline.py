from datetime import date, timedelta

from sqlmodel import Session

from app.core.db import sync_engine
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.web_harvester.crawler import NewsAPICrawler
from app.services.web_harvester.crawler_scraper import SeparateCrawlerScraper
from app.services.web_harvester.scraper import TrafilaturaScraper

if __name__ == "__main__":
    with Session(sync_engine) as session:
        horizont = SubscriptionRepository.get_subscription_by_id(
            session=session,
            subscription_id="bf210331-e2e7-4912-8eca-c3276d44ff15",
        )
        a = SeparateCrawlerScraper(
            session=session,
            crawler=NewsAPICrawler(),
            scraper=TrafilaturaScraper(),
        ).crawl_and_scrape(subscription=horizont, skip_crawling=True)
        print(a)
