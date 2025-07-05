from datetime import date
from typing import List

from app.core.logger import get_logger
from app.repositories.crawl_stats_repository import CrawlStatsRepository
from app.schemas.crawl_stats_schemas import CrawlStatsItem

logger = get_logger(__name__)


class CrawlStatsService:
    """Service layer for crawl statistics operations."""

    @staticmethod
    async def get_crawl_stats_by_date(
        crawl_date: date,
    ) -> List[CrawlStatsItem]:
        """
        Get crawl statistics for a specific date.

        Args:
            crawl_date: The date to get crawl stats for

        Returns:
            List of CrawlStatsItem with subscription names
        """
        crawl_stats = await CrawlStatsRepository.get_crawl_stats_by_date(
            crawl_date
        )

        result = []
        for stat in crawl_stats:
            # Get subscription name from the relationship
            subscription_name = (
                stat.subscription.name if stat.subscription else "Unknown"
            )

            result.append(
                CrawlStatsItem(
                    subscription_name=subscription_name,
                    total_successful=stat.total_successful,
                    total_attempted=stat.total_attempted,
                    crawl_date=stat.crawl_date,
                    notes=stat.notes,
                )
            )

        logger.info(
            f"Retrieved {len(result)} crawl stats for date {crawl_date}"
        )
        return result

    @staticmethod
    async def get_crawl_stats_by_date_range(
        date_start: date, date_end: date
    ) -> List[CrawlStatsItem]:
        """
        Get crawl statistics for a date range.

        Args:
            date_start: Start date for the range
            date_end: End date for the range

        Returns:
            List of CrawlStatsItem with subscription names
        """
        crawl_stats = await CrawlStatsRepository.get_crawl_stats_by_date_range(
            date_start, date_end
        )

        result = []
        for stat in crawl_stats:
            # Get subscription name from the relationship
            subscription_name = (
                stat.subscription.name if stat.subscription else "Unknown"
            )

            result.append(
                CrawlStatsItem(
                    subscription_name=subscription_name,
                    total_successful=stat.total_successful,
                    total_attempted=stat.total_attempted,
                    crawl_date=stat.crawl_date,
                    notes=stat.notes[:1000] if stat.notes else None,
                )
            )

        logger.info(
            f"Retrieved {len(result)} crawl stats for date range "
            f"{date_start} to {date_end}"
        )
        return result
