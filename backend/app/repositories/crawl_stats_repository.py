from datetime import date, timedelta
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import selectinload

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
    async def get_crawl_stats_last_day() -> list[CrawlStats]:
        async with async_session() as session:
            today = date.today()
            yesterday = today - timedelta(days=1)
            result = await session.execute(
                sa.select(CrawlStats)
                .where(CrawlStats.crawl_date >= yesterday)
                .options(selectinload(CrawlStats.subscription))
            )
            return result.scalars().all()
