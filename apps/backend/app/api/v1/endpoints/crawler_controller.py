"""
NOTE:
This is just a testing controller for crawling and scraping.
Once we have a proper scheduler, we can remove this controller.
"""

from datetime import date
from datetime import date as Date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.schemas.breaking_news_schemas import (
    BreakingNewsItem,
    BreakingNewsResponse,
)
from app.schemas.crawl_stats_schemas import CrawlStatsResponse
from app.schemas.user_schema import UserEntity
from app.services.crawl_stats_service import CrawlStatsService
from app.services.web_harvester.breaking_news_crawler import (
    get_all_breaking_news,
)

router = APIRouter(
    prefix="/crawler",
    tags=["crawler"],
)

logger = get_logger(__name__)


@router.get("/get_breaking_news", response_model=BreakingNewsResponse)
async def get_breaking_news():
    breaking_news = get_all_breaking_news()
    news_items = [BreakingNewsItem.from_entity(news) for news in breaking_news]
    return BreakingNewsResponse(news=news_items, total_count=len(news_items))


@router.get("/stats", response_model=CrawlStatsResponse)
async def get_crawl_stats(
    date_start: Optional[Date] = Query(
        None, description="Start date for date range query (YYYY-MM-DD)"
    ),
    date_end: Optional[Date] = Query(
        None, description="End date for date range query (YYYY-MM-DD)"
    ),
    current_user: UserEntity = Depends(get_authenticated_user),
):
    """
    Get crawler statistics based on date criteria.
    - If `date_start` and `date_end` are provided, returns stats for that range
    - If no parameters are provided, returns stats for today
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
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
