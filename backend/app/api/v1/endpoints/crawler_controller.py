"""
NOTE:
This is just a testing controller for crawling and scraping.
Once we have a proper scheduler, we can remove this controller.
"""

import asyncio
from datetime import date
from datetime import date as Date
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.core.logger import get_logger
from app.schemas.breaking_news_schemas import (
    BreakingNewsItem,
    BreakingNewsResponse,
)
from app.schemas.crawl_stats_schemas import CrawlStatsResponse
from app.services import pipeline
from app.services.crawl_stats_service import CrawlStatsService
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


@router.post("/trigger_rss_crawling")
async def trigger_rss_crawling(
    datetime_start: datetime = datetime.combine(
        date.today(), datetime.min.time()
    ),
    datetime_end: datetime = datetime.now(),
):
    logger.info(
        f"Triggering RSS crawling from {datetime_start} to {datetime_end}"
    )
    asyncio.create_task(
        run_crawler(
            CrawlerType.RSSFeedCrawler,
            date_start=datetime_start,
            date_end=datetime_end,
            limit=-1,
        )
    )
    return {"message": "RSS Crawling triggered successfully"}


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


@router.post("/trigger_pipeline")
async def trigger_pipeline(
    datetime_start: datetime = datetime.combine(
        date.today(), datetime.min.time()
    ),
    datetime_end: datetime = datetime.now(),
    language: str = "en",
):

    logger.info(f"Triggering pipeline from {datetime_start} to {datetime_end}")
    asyncio.create_task(
        pipeline.run(
            datetime_start=datetime_start,
            datetime_end=datetime_end,
            language=language,
        )
    )
    return {"message": "Pipeline triggered successfully"}


@router.get("/stats", response_model=CrawlStatsResponse)
async def get_crawl_stats(
    date_start: Optional[Date] = Query(
        None, description="Start date for date range query (YYYY-MM-DD)"
    ),
    date_end: Optional[Date] = Query(
        None, description="End date for date range query (YYYY-MM-DD)"
    ),
):
    """
    Get crawler statistics based on date criteria.
    - If `date_start` and `date_end` are provided, returns stats for that range
    - If no parameters are provided, returns stats for today
    """
    if date_start and date_end:
        # Get stats for date range
        stats = await CrawlStatsService.get_crawl_stats_by_date_range(
            date_start, date_end
        )
        logger.info(
            f"Retrieved crawl stats for range {date_start} to {date_end}"
        )
    else:
        # Default to today
        today = date.today()
        stats = await CrawlStatsService.get_crawl_stats_by_date_range(
            today, today
        )
        logger.info(f"Retrieved crawl stats for today ({today})")

    return CrawlStatsResponse(stats=stats, total_count=len(stats))
