from typing import List, Optional, Sequence
from uuid import UUID

from langchain_core.documents import Document
from sqlmodel import select
from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.db import async_session
from app.models import ArticleKeywordLink, Keyword
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.services.article_vector_service import ArticleVectorService
from app.models import User
from app.models.keyword import Keyword
from app.models.topic import Topic
from app.schemas.keyword_schemas import KeywordCreateRequest

article_vector_service = ArticleVectorService()


class KeywordRepository:
    """Repository for managing Keyword entities in the database."""

    @staticmethod
    async def get_keyword_by_id(keyword_id: UUID) -> Optional[Keyword]:
        """Retrieve a single Keyword by its UUID."""
        async with async_session() as session:
            statement = select(Keyword).where(Keyword.id == keyword_id)
            keyword: Optional[Keyword] = (
                await session.execute(statement)
            ).scalar_one_or_none()

            return keyword
    async def get_or_create_keyword(
        session: AsyncSession, name: str
    ) -> Keyword:
        result = await session.execute(
            select(Keyword).where(Keyword.name == name)
        )
        keyword = result.scalar_one_or_none()
        if keyword:
            return keyword
        keyword = Keyword(name=name)
        session.add(keyword)
        await session.commit()
        await session.refresh(keyword)
        return keyword

    @staticmethod
    async def list_keywords(
        limit: int = 100, offset: int = 0
    ) -> Sequence[Keyword]:
        """Retrieve a list of keywords with pagination."""
    async def get_keywords_by_topic(
        topic_id: UUID, user: User
    ) -> list[Keyword]:
        async with async_session() as session:
            statement = select(Keyword).limit(limit).offset(offset)
            result = await session.execute(statement)
            keywords = result.scalars().all()
            return keywords
            query = (
                select(Keyword)
                .join(Topic)
                .where(
                    Keyword.topic_id == topic_id,
                    Topic.search_profile.has(user_id=user.id),
                )
            )
            keywords = await session.execute(query)
            return keywords.scalars().all()

    @staticmethod
    async def add_keyword(keyword: str) -> Keyword:
        """Add a new keyword to the database."""
        new_keyword = Keyword(name=keyword)
    async def add_keyword(
        topic_id: UUID, request: KeywordCreateRequest, user: User
    ) -> Keyword:
        async with async_session() as session:
            session.add(new_keyword)
            topic = await session.get(
                Topic, topic_id, options=[joinedload(Topic.search_profile)]
            )
            if topic is None or topic.search_profile.user_id != user.id:
                raise HTTPException(status_code=403, detail="Not authorized")

            keyword = Keyword(value=request.value, topic_id=topic_id)
            session.add(keyword)
            await session.commit()
            await session.refresh(new_keyword)
            return new_keyword
            await session.refresh(keyword)
            return keyword

    @staticmethod
    async def add_article_to_keyword(
        keyword_id: UUID, article_id: UUID, score: float
    ) -> None:
        """Assign an article to a keyword with a similarity score."""
    async def delete_keyword(
        topic_id: UUID, keyword_id: UUID, user: User
    ) -> bool:
        async with async_session() as session:

            link = ArticleKeywordLink(
                article_id=article_id, keyword_id=keyword_id, score=score
            query = delete(Keyword).where(
                Keyword.id == keyword_id,
                Keyword.topic_id == topic_id,
                Keyword.topic.has(search_profile__user_id=user.id),
            )
            session.add(link)

            keywords = await session.execute(query)
            await session.commit()
            return keywords.rowcount > 0

    @staticmethod
    async def get_similar_articles_by_keyword_id(
        keyword_id: UUID, score_threshold: float = 0.3
    ) -> List[Article]:
        """Retrieve the most similar articles for a given keyword."""

        keyword = await KeywordRepository.get_keyword_by_id(keyword_id)
        if not keyword:
            raise ValueError(f"Keyword with id {keyword_id} not found.")
        similarity_results = (
            await article_vector_service.retrieve_by_similarity(
                keyword.name, score_threshold=score_threshold
            )
        )

        similar_articles: List[Article] = []
        for doc, score in similarity_results:
            article_id = doc.metadata["id"]
            article: Optional[Article] = (
                await ArticleRepository.get_article_by_id(article_id)
            )
            if article:
                similar_articles.append(article)
            else:
                raise ValueError(
                    f"Article with id {article_id} not found in the database."
                )

        return similar_articles

    @staticmethod
    async def assign_articles_to_keywords(
        page_size: int = 100, score_threshold: float = 0.3
    ) -> None:
        """
        Assign articles to all keywords based on similarity scores.
        Args:
            page_size: int = 100: Number of keywords to process in each batch.
            score_threshold: float: Minimum score threshold for similarity.
        """
        page = 0
        keywords: Sequence[Keyword] = await KeywordRepository.list_keywords(
            limit=page_size, offset=page * page_size
        )

        while keywords:
            for keyword in keywords:
                similar_articles: List[tuple[Document, float]] = (
                    await article_vector_service.retrieve_by_similarity(
                        query=keyword.name, score_threshold=score_threshold
                    )
                )

                for doc, score in similar_articles:
                    await KeywordRepository.add_article_to_keyword(
                        keyword.id, doc.metadata["id"], score
                    )

            page += 1
            keywords = await KeywordRepository.list_keywords(
                limit=page_size, offset=page * page_size
            )
