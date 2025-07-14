"""
Article Cleanup Service

This service is responsible for deleting
articles older than a specified number of days
along with all their related data to maintain
database hygiene and manage storage costs.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlalchemy import delete, select

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
        self, days: int = 180, batch_size: int = 100
    ) -> dict:
        """
        Delete articles older than the specified
        number of days along with all related data.

        Args:
            days: Number of days to look back for article deletion
            batch_size: Number of articles to process in each batch

        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        logger.info(
            f"Starting article cleanup for articles older than {cutoff_date}"
        )

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

            # Process articles in batches
            offset = 0
            while offset < total_articles:
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
            f"Article cleanup completed. "
            f"Stats: {stats['articles_deleted']} articles deleted, "
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
