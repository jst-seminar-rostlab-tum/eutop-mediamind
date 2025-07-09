from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models.crawl_stats import CrawlStats

logger = get_logger(__name__)


class CrawlStatsRepository:
    @staticmethod
    async def insert_crawl_stats(
        crawl_stats: CrawlStats,
    ) -> Optional[CrawlStats]:
        async with async_session() as session:
            try:
                session.add(crawl_stats)
                await session.commit()
                await session.refresh(crawl_stats)
                return crawl_stats
            except Exception as e:
                logger.error(f"Failed to insert crawl stats: {e}")
                await session.rollback()
                return None

    @staticmethod
    async def get_crawl_stats_by_date_range(
        date_start: date,
        date_end: date,
    ) -> List[CrawlStats]:
        """Get crawl stats for a date range."""
        async with async_session() as session:
            try:
                stmt = (
                    select(CrawlStats)
                    .options(joinedload(CrawlStats.subscription))
                    .where(
                        CrawlStats.crawl_date >= date_start,
                        CrawlStats.crawl_date <= date_end,
                    )
                    .order_by(
                        CrawlStats.crawl_date, CrawlStats.subscription_id
                    )
                )
                result = await session.execute(stmt)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Failed to get crawl stats by date range: {e}")
                return []
