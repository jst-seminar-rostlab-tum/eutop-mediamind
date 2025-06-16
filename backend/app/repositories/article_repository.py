from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import desc, or_, select
from sqlalchemy.orm.strategy_options import joinedload

from sqlalchemy.exc import IntegrityError
from app.core.db import async_session
from app.core.logger import get_logger
from app.models.article import Article

logger = get_logger(__name__)


class ArticleRepository:
    """Repository for managing Article entities in the database."""

    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Optional[Article]:
        """
        Retrieve a single Article by its UUID.
        Returns None if no article is found.
        """

        async with async_session() as session:
            statement = select(Article).where(Article.id == article_id)
            article: Optional[Article] = (
                await session.execute(statement)
            ).scalar_one_or_none()
            return article

    @staticmethod
    async def update_article(article: Article) -> Optional[Article]:
        """
        Update an existing Article in the database.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing_article = await session.get(Article, article.id)
            if not existing_article:
                return None

            existing_article_without_id = article.model_dump(
                exclude_unset=True, exclude={"id"}
            )
            for key, val in existing_article_without_id.items():
                setattr(existing_article, key, val)

            session.add(existing_article)
            await session.commit()
            await session.refresh(existing_article)
            return existing_article

    @staticmethod
    async def update_article_summary(
        article_id: UUID, article_summary: str
    ) -> Optional[Article]:
        """
        Update only the 'summary' field of an existing Article.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing_article = await session.get(Article, article_id)
            if not existing_article:
                return None

            existing_article.summary = article_summary
            session.add(existing_article)
            await session.commit()
            await session.refresh(existing_article)
            return existing_article

    @staticmethod
    async def create_article(article: Article) -> Article:
        """
        Add a new Article to the database.
        """
        async with async_session() as session:
            try:
                session.add(article)
                await session.commit()
                await session.refresh(article)
                return article
            except Exception as e:
                print(e)
                return

    @staticmethod
    async def create_articles_batch(
        articles: list[Article], batch_size: int = 50
    ):
        successful = []
        async with async_session() as session:
            for i in range(0, len(articles), batch_size):
                batch = articles[i : i + batch_size]
                try:
                    session.add_all(batch)
                    await session.commit()
                    successful.extend(batch)
                except Exception:
                    await session.rollback()
                    logger.warning("Batch failed, inserting individual now")

                    # Try inserting articles one-by-one
                    for article in batch:
                        try:
                            session.add(article)
                            await session.commit()
                            successful.append(article)
                        except IntegrityError as e:
                            await session.rollback()
                            if (
                                hasattr(e.orig, "sqlstate")
                                and e.orig.sqlstate == "23505"
                            ):
                                error_detail = str(e.orig)
                                # Check if it's specifically the URL constraint
                                if (
                                    "duplicate key value violates unique "
                                    'constraint "articles_url_key"'
                                    in error_detail
                                ):
                                    logger.warning(
                                        f"Article with URL {article.url} "
                                        "already exists, skipping."
                                    )
                                    continue
                            logger.error(f"Failed to insert article: {e}")
                            continue
                        except Exception as e:
                            logger.error(
                                f"Failed to insert article {article.url}: {e}"
                            )
                            await session.rollback()

        return successful

    @staticmethod
    async def list_articles(
        limit: int = 100, offset: int = 0, set_of: int = 0
    ) -> Sequence[Article]:
        """
        List articles with optional pagination and batch processing.
        """
        async with async_session() as session:
            statement = (
                select(Article).limit(limit).offset(offset + (set_of * limit))
            )
            articles: list[Article] = (
                (await session.execute(statement)).scalars().all()
            )
            return articles

    @staticmethod
    async def list_articles_without_summary(
        limit: int = 100, offset: int = 0
    ) -> Sequence[Article]:
        """
        List articles that have no summary yet, with pagination.
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(or_(Article.summary.is_(None), Article.summary == ""))
                .limit(limit)
                .offset(offset)
            )
            unsummarized_articles: Sequence[Article] = (
                (await session.execute(statement)).scalars().all()
            )

            return unsummarized_articles

    @staticmethod
    async def list_articles_with_summary(
        limit: int = 100, offset: int = 0
    ) -> Sequence[Article]:
        """
        List articles that have a summary, with pagination.
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(Article.summary.isnot(None), Article.summary != "")
                .limit(limit)
                .offset(offset)
            )
            summarized_articles: Sequence[Article] = (
                (await session.execute(statement)).scalars().all()
            )

            return summarized_articles

    @staticmethod
    async def get_sameple_articles(limit: int) -> List[Article]:
        async with async_session() as session:
            result = await session.execute(
                select(Article)
                .order_by(desc(Article.published_at))
                .limit(limit)
                .options(joinedload("*"))
            )
            return result.unique().scalars().all()
