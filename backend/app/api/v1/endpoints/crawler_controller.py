"""
NOTE:
This is just a testing controller for crawling and scraping.
Once we have a proper scheduler, we can remove this controller.
"""

import asyncio
from datetime import date
from datetime import date as Date

from fastapi import APIRouter

from app.core.logger import get_logger
from app.services.web_harvester.crawler import CrawlerType
from app.services.web_harvester.pipeline import run_crawler, run_scraper

router = APIRouter(
    prefix="/crawler",
    tags=["crawler"],
)

logger = get_logger(__name__)


@router.post("/trigger_crawling")
async def trigger_crawling(
    date_start: Date = date.today(), date_end: Date = date.today()
):
    logger.info(f"Triggering crawling from {date_start} to {date_end}")
    asyncio.create_task(
        run_crawler(
            CrawlerType.NewsAPICrawler,
            date_start=date_start,
            date_end=date_end,
        )
    )
    return {"message": "Crawling triggered successfully"}


@router.post("/trigger_scraping")
async def trigger_scraping():
    logger.info("Triggering scraping")
    asyncio.create_task(run_scraper())
    return {"message": "Scraping triggered successfully"}
