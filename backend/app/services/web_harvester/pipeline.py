from app.services.web_harvester.crawler import NewsAPICrawler
from app.services.web_harvester.scraper import TrafilaturaScraper
from app.services.web_harvester.crawler_scraper import SeparateCrawlerScraper
from app.core.db import engine
from sqlmodel import Session
from datetime import date, timedelta


from app.repositories.subscription_repository import SubscriptionRepository


if __name__ == "__main__":
    with Session(engine) as session:
        horizont = SubscriptionRepository.get_subscription_by_id(
            session=session, subscription_id="60e6484f-449f-4d68-a110-ec2dbfd138a8"
        )
        a = SeparateCrawlerScraper(
            session=session,  # Replace with actual session
            crawler=NewsAPICrawler(),
            scraper=TrafilaturaScraper()  # Replace with actual scraper
        ).crawl_and_scrape(subscription=horizont, skip_crawling=True)  # Replace with actual subscription
        print(a)
