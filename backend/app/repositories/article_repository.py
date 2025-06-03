from typing import Sequence, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.models.article import Article
from app.core.db import engine, async_session
from sqlalchemy import or_

class ArticleRepository:
    @staticmethod
    async def get_article_by_id(article_id: UUID) -> Optional[Article]:
        """
        Retrieve a single Article by its UUID.
        Returns None if no article is found.
        """
        # 1) asynchronen Kontext starten
        async with async_session() as session:
            statement = select(Article).where(Article.id == article_id)
            result = await session.execute(statement)
            return result.scalars().first()

    async def update_article(article: Article) -> Optional[Article]:
        """
        Update an existing Article in the database.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing = await session.get(Article, article.id)
            if not existing:
                return None

            # Nur die gesetzten Felder aus new_data extrahieren
            existing_data = article.model_dump(exclude_unset=True, exclude={"id"})
            for key, val in existing_data.items():
                setattr(existing, key, val)

            session.add(existing)
            await session.commit()
            await session.refresh(existing)
            return existing

    @staticmethod
    async def update_summary(article_id: UUID, summary: str) -> Optional[Article]:
        """
        Update only the 'summary' field of an existing Article.
        Returns the updated Article, or None if it does not exist.
        """
        async with async_session() as session:
            existing = await session.get(Article, article_id)
            if not existing:
                return None

            existing.summary = summary
            session.add(existing)
            await session.commit()
            await session.refresh(existing)
            return existing

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
                select(Article)
                .limit(limit)
                .offset(offset + (set_of * limit))
            )
            result = await session.execute(statement)
            return result.scalars().all()

    @staticmethod
    async def list_articles_without_summary(limit: int = 100, offset: int = 0) -> Sequence[Article]:
        """
        List articles that have no summary yet, with pagination.
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(
                    or_(
                        Article.summary.is_(None),
                        Article.summary == ""
                    )
                )
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(statement)
            articles = result.scalars().all()
            print(f"Found {len(articles)} articles without summary.")
            return articles

    @staticmethod
    async def list_articles_with_summary(limit: int = 100, offset: int = 0) -> Sequence[Article]:
        """
        Listet Artikel, bei denen das Feld `summary` nicht NULL und nicht leer ist,
        mit Pagination (limit/offset).
        """
        async with async_session() as session:
            statement = (
                select(Article)
                .where(
                    Article.summary.isnot(None),
                    Article.summary != ""
                )
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(statement)
            return result.scalars().all()