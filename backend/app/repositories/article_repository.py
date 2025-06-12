from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from sqlmodel import select
from sqlmodel import Session

from app.core.logger import get_logger
from app.core.db import async_session
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
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article

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

    def update_article(session: Session, article: Article) -> Article:
        existing_article = session.get(Article, article.id)
        if existing_article:
            for attr, value in vars(article).items():
                if attr != "_sa_instance_state":
                    setattr(existing_article, attr, value)
            session.commit()
            session.refresh(existing_article)
            return existing_article
        else:
            return None

    @staticmethod
    def insert_articles(articles: list[Article], session) -> list[Article]:
        inserted_articles = []
        for article in articles:
            try:
                session.add(article)
                session.commit()
                session.refresh(article)
                inserted_articles.append(article)
            except IntegrityError as e:
                session.rollback()  # Roll back the failed transaction
                if hasattr(e.orig, "sqlstate") and e.orig.sqlstate == "23505":
                    error_detail = str(e.orig)
                    # Check if it's specifically the URL constraint
                    if (
                        "articles_url_key" in error_detail
                        or 'duplicate key value violates unique constraint "articles_url_key"'
                        in error_detail
                    ):
                        logger.warning(
                            f"Article with URL {article.url} already exists, skipping."
                        )
                        continue
                    else:
                        # Other unique constraint violation
                        logger.error(f"Unique constraint violation: {e}")
                        continue
                else:
                    # Other integrity error
                    logger.error(f"Failed to insert article: {e}")
                    continue
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to insert article: {e}")
                continue
        return inserted_articles

    @staticmethod
    def get_articles_by_subscription_with_empty_content(
        session, subscription_id: str
    ) -> list[Article]:
        result = session.execute(
            select(Article)
            .where(Article.subscription_id == subscription_id)
            .where(Article.content.is_(None))
        )
        return result.scalars().all()
