from typing import Optional

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
