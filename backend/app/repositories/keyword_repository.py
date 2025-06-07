from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.db import async_session, engine
from app.models import ArticleKeywordLink, Keyword
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.services.article_vector_service import ArticleVectorService

article_vector_service = ArticleVectorService()


class KeywordRepository:

    @staticmethod
    async def get_keyword_by_id(keyword_id: UUID) -> Optional[Keyword]:
        """Retrieve a single Keyword by its UUID."""
        async with async_session() as session:
            statement = select(Keyword).where(Keyword.id == keyword_id)
            keyword: Optional[Keyword] = (
                await session.execute(statement)
            ).scalar_one_or_none()

            return keyword

    @staticmethod
    async def list_keywords(
        limit: int = 100, offset: int = 0
    ) -> Sequence[Keyword]:
        """Retrieve a list of keywords with pagination."""
        async with async_session() as session:
            statement = select(Keyword).limit(limit).offset(offset)
            result = await session.execute(statement)
            keywords = result.scalars().all()
            return keywords

    @staticmethod
    async def add_keyword(keyword: str) -> Keyword:
        """Add a new keyword to the database."""
        new_keyword = Keyword(name=keyword)
        async with async_session() as session:
            session.add(new_keyword)
            await session.commit()
            await session.refresh(new_keyword)
            return new_keyword

    @staticmethod
    async def add_article_to_keyword(
        keyword_id: UUID, article_id: UUID, score: float
    ) -> None:
        """Assign an article to a keyword und speichere dabei den score in der Link-Tabelle."""
        async with async_session() as session:

            link = ArticleKeywordLink(
                article_id=article_id, keyword_id=keyword_id, score=score
            )
            session.add(link)

            await session.commit()

    @staticmethod
    async def get_similar_articles_by_keyword_id(
        keyword_id: UUID, score_threshold: float = 0.3
    ) -> List[Article]:
        """Retrieve the most similar articles for a given keyword."""

        keyword = await KeywordRepository.get_keyword_by_id(keyword_id)
        if not keyword:
            raise ValueError(f"Keyword with id {keyword_id} not found.")
        similarity_results = await article_vector_service.retrieve_by_similarity(
            keyword.name, score_threshold=score_threshold
        )

        similar_articles: List[Article] = []
        for doc, score in similarity_results:
            article_id = doc.metadata["id"]
            article: Optional[Article] = await ArticleRepository.get_article_by_id(
                article_id
            )
            if article:
                similar_articles.append(article)
            else:
                raise ValueError(
                    f"Article with id {article_id} not found in the database."
                )

        return similar_articles

    @staticmethod
    async def assign_articles_to_keywords(page_size: int = 100, score_threshold: float = 0.3) -> None:
        page = 0
        keywords: List[Keyword] = await KeywordRepository.list_keywords(
            limit=page_size, offset=page * page_size
        )

        while keywords:
            for keyword in keywords:
                similar_articles: List[Article] = await article_vector_service.retrieve_by_similarity(
                    query=keyword.name,
                    score_threshold=score_threshold
                )

                for doc, score in similar_articles:
                await KeywordRepository.add_article_to_keyword(
                    keyword.id,
                    doc.metadata["id"],
                    score
                )

            page += 1
            keywords = await KeywordRepository.list_keywords(
                limit=page_size, offset=page * page_size
            )
            
