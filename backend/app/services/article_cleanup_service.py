"""
Article Cleanup Service

This service is responsible for deleting articles older than a specified number of days
along with all their related data to maintain database hygiene and manage storage costs.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, func, select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models.article import Article
from app.models.associations import ArticleKeywordLink
from app.models.entity import ArticleEntity
from app.models.match import Match
from app.services.article_vector_service import ArticleVectorService

logger = get_logger(__name__)


class ArticleCleanupService:
    """Service for cleaning up old articles and their related data."""

    def __init__(self):
        self.vector_service = ArticleVectorService()

    async def cleanup_articles_older_than_days(
        self, days: int = 180, batch_size: int = 100, dry_run: bool = False
    ) -> dict:
        """
        Delete articles older than the specified number of days along with all related data.

        Args:
            days: Number of days to look back for article deletion (default: 180)
            batch_size: Number of articles to process in each batch (default: 100)
            dry_run: If True, only count articles but don't delete them

        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        logger.info(
            f"Starting article cleanup for articles older than {cutoff_date}"
        )
        if dry_run:
            logger.info("Running in DRY RUN mode - no data will be deleted")

        stats = {
            "articles_processed": 0,
            "articles_deleted": 0,
            "entities_deleted": 0,
            "keyword_links_deleted": 0,
            "matches_deleted": 0,
            "vector_store_deletions": 0,
            "errors": 0,
            "cutoff_date": cutoff_date.isoformat(),
        }

        try:
            # Get total count first
            async with async_session() as session:
                count_stmt = select(Article).where(
                    Article.published_at < cutoff_date
                )
                count_result = await session.execute(count_stmt)
                total_articles = len(count_result.scalars().all())

            logger.info(f"Found {total_articles} articles to process")

            if dry_run:
                stats["articles_processed"] = total_articles
                logger.info(
                    f"DRY RUN: Would delete {total_articles} articles and their related data"
                )
                return stats

            # Process articles in batches
            offset = 0
            while True:
                batch_stats = await self._process_article_batch(
                    cutoff_date, batch_size, offset
                )

                if batch_stats["batch_size"] == 0:
                    break

                # Update overall stats
                for key in [
                    "articles_deleted",
                    "entities_deleted",
                    "keyword_links_deleted",
                    "matches_deleted",
                    "vector_store_deletions",
                    "errors",
                ]:
                    stats[key] += batch_stats[key]

                stats["articles_processed"] += batch_stats["batch_size"]

                logger.info(
                    f"Processed batch {offset//batch_size + 1}: "
                    f"{batch_stats['articles_deleted']} articles deleted, "
                    f"{batch_stats['errors']} errors"
                )

                offset += batch_size

        except Exception as e:
            logger.error(f"Error during article cleanup: {e}")
            stats["errors"] += 1
            raise

        logger.info(
            f"Article cleanup completed. Stats: {stats['articles_deleted']} articles deleted, "
            f"{stats['entities_deleted']} entities deleted, "
            f"{stats['keyword_links_deleted']} keyword links deleted, "
            f"{stats['matches_deleted']} matches deleted, "
            f"{stats['vector_store_deletions']} vector store entries deleted, "
            f"{stats['errors']} errors"
        )

        return stats

    async def _process_article_batch(
        self, cutoff_date: datetime, batch_size: int, offset: int
    ) -> dict:
        """Process a batch of articles for deletion."""
        batch_stats = {
            "batch_size": 0,
            "articles_deleted": 0,
            "entities_deleted": 0,
            "keyword_links_deleted": 0,
            "matches_deleted": 0,
            "vector_store_deletions": 0,
            "errors": 0,
        }

        async with async_session() as session:
            try:
                # Get batch of articles with their IDs
                stmt = (
                    select(Article)
                    .where(Article.published_at < cutoff_date)
                    .limit(batch_size)
                    .offset(offset)
                )
                result = await session.execute(stmt)
                articles = result.scalars().all()

                batch_stats["batch_size"] = len(articles)

                if not articles:
                    return batch_stats

                article_ids = [article.id for article in articles]

                # Delete related data first (to maintain referential integrity)

                # 1. Delete article entities
                entities_deleted = await self._delete_article_entities(
                    session, article_ids
                )
                batch_stats["entities_deleted"] = entities_deleted

                # 2. Delete article-keyword links
                keyword_links_deleted = (
                    await self._delete_article_keyword_links(
                        session, article_ids
                    )
                )
                batch_stats["keyword_links_deleted"] = keyword_links_deleted

                # 3. Delete matches
                matches_deleted = await self._delete_article_matches(
                    session, article_ids
                )
                batch_stats["matches_deleted"] = matches_deleted

                # 4. Delete from vector store
                vector_deletions = await self._delete_from_vector_store(
                    article_ids
                )
                batch_stats["vector_store_deletions"] = vector_deletions

                # 5. Finally, delete the articles themselves
                articles_deleted = await self._delete_articles(
                    session, article_ids
                )
                batch_stats["articles_deleted"] = articles_deleted

                await session.commit()

            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Error processing article batch at offset {offset}: {e}"
                )
                batch_stats["errors"] += 1

        return batch_stats

    async def _delete_article_entities(
        self, session, article_ids: List[UUID]
    ) -> int:
        """Delete all entities associated with the given articles."""
        if not article_ids:
            return 0

        stmt = delete(ArticleEntity).where(
            ArticleEntity.article_id.in_(article_ids)
        )
        result = await session.execute(stmt)
        deleted_count = result.rowcount

        logger.debug(f"Deleted {deleted_count} article entities")
        return deleted_count

    async def _delete_article_keyword_links(
        self, session, article_ids: List[UUID]
    ) -> int:
        """Delete all keyword links associated with the given articles."""
        if not article_ids:
            return 0

        stmt = delete(ArticleKeywordLink).where(
            ArticleKeywordLink.article_id.in_(article_ids)
        )
        result = await session.execute(stmt)
        deleted_count = result.rowcount

        logger.debug(f"Deleted {deleted_count} article-keyword links")
        return deleted_count

    async def _delete_article_matches(
        self, session, article_ids: List[UUID]
    ) -> int:
        """Delete all matches associated with the given articles."""
        if not article_ids:
            return 0

        stmt = delete(Match).where(Match.article_id.in_(article_ids))
        result = await session.execute(stmt)
        deleted_count = result.rowcount

        logger.debug(f"Deleted {deleted_count} article matches")
        return deleted_count

    async def _delete_from_vector_store(self, article_ids: List[UUID]) -> int:
        """Delete articles from the vector store."""
        if not article_ids:
            return 0

        try:
            # Convert UUIDs to strings for vector store
            article_id_strings = [
                str(article_id) for article_id in article_ids
            ]

            # Delete from vector store using the new method
            deleted_count = self.vector_service.delete_articles_by_ids(
                article_id_strings
            )

            logger.debug(f"Deleted {deleted_count} articles from vector store")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting from vector store: {e}")
            return 0

    async def _delete_articles(self, session, article_ids: List[UUID]) -> int:
        """Delete the articles themselves."""
        if not article_ids:
            return 0

        stmt = delete(Article).where(Article.id.in_(article_ids))
        result = await session.execute(stmt)
        deleted_count = result.rowcount

        logger.debug(f"Deleted {deleted_count} articles")
        return deleted_count

    async def get_cleanup_preview(self, days: int = 180) -> dict:
        """
        Get a preview of what would be deleted without actually deleting anything.

        Args:
            days: Number of days to look back for article deletion

        Returns:
            Dict with preview statistics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            logger.info(
                f"Getting cleanup preview for articles older than {cutoff_date}"
            )

            async with async_session() as session:
                # Count articles to be deleted
                article_stmt = select(Article).where(
                    Article.published_at < cutoff_date
                )
                article_result = await session.execute(article_stmt)
                articles = article_result.scalars().all()
                article_ids = [article.id for article in articles]

                logger.debug(
                    f"Found {len(articles)} articles older than {cutoff_date}"
                )

                # If no articles found, return early with zero counts
                if not article_ids:
                    logger.info("No articles found to delete")
                    return {
                        "cutoff_date": cutoff_date.isoformat(),
                        "articles_to_delete": 0,
                        "entities_to_delete": 0,
                        "keyword_links_to_delete": 0,
                        "matches_to_delete": 0,
                        "oldest_article_date": None,
                        "newest_article_date": None,
                    }

                # Count related entities
                if article_ids:
                    entity_stmt = select(func.count(ArticleEntity.id)).where(
                        ArticleEntity.article_id.in_(article_ids)
                    )
                    entity_result = await session.execute(entity_stmt)
                    entity_count = entity_result.scalar() or 0

                    # Count keyword links
                    keyword_stmt = select(
                        func.count(ArticleKeywordLink.article_id)
                    ).where(ArticleKeywordLink.article_id.in_(article_ids))
                    keyword_result = await session.execute(keyword_stmt)
                    keyword_count = keyword_result.scalar() or 0

                    # Count matches
                    match_stmt = select(func.count(Match.id)).where(
                        Match.article_id.in_(article_ids)
                    )
                    match_result = await session.execute(match_stmt)
                    match_count = match_result.scalar() or 0
                else:
                    entity_count = 0
                    keyword_count = 0
                    match_count = 0

                # Get date range for the articles to be deleted
                oldest_date = None
                newest_date = None
                if articles:
                    valid_dates = [
                        a.published_at
                        for a in articles
                        if a.published_at is not None
                    ]
                    if valid_dates:
                        oldest_date = min(valid_dates).isoformat()
                        newest_date = max(valid_dates).isoformat()

                result = {
                    "cutoff_date": cutoff_date.isoformat(),
                    "articles_to_delete": len(articles),
                    "entities_to_delete": entity_count,
                    "keyword_links_to_delete": keyword_count,
                    "matches_to_delete": match_count,
                    "oldest_article_date": oldest_date,
                    "newest_article_date": newest_date,
                }

                logger.info(
                    f"Cleanup preview: {result['articles_to_delete']} articles, {result['entities_to_delete']} entities, {result['keyword_links_to_delete']} keyword links, {result['matches_to_delete']} matches"
                )
                return result

        except Exception as e:
            logger.error(f"Error getting cleanup preview: {e}")
            raise
