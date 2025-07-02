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
from app.schemas.breaking_news_schemas import (
    BreakingNewsItem,
    BreakingNewsResponse,
)
from app.services.web_harvester.breaking_news_crawler import (
    fetch_breaking_news_newsapi,
    get_all_breaking_news,
)
from app.services.web_harvester.crawler import CrawlerType
from app.services.web_harvester.web_harvester_orchestrator import (
    run_crawler,
    run_scraper,
)

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


@router.post("/trigger_breaking_news_crawling")
async def trigger_newsapi_crawling():
    logger.info("Triggering breaking news crawling")
    breaking_news = fetch_breaking_news_newsapi()
    return {"message": f"Crawled {len(breaking_news)} breaking news articles"}


@router.get("/get_breaking_news", response_model=BreakingNewsResponse)
async def get_breaking_news():
    breaking_news = get_all_breaking_news()
    news_items = [BreakingNewsItem.from_entity(news) for news in breaking_news]
    return BreakingNewsResponse(news=news_items, total_count=len(news_items))
