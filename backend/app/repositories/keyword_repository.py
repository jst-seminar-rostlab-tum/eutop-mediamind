from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Keyword, ArticleKeywordLink
from app.models.article import Article
from app.core.db import engine, async_session
from sqlalchemy import or_

from app.repositories.article_repository import ArticleRepository
from app.services.article_vector_service import ArticleVectorService

article_vector_service = ArticleVectorService()

class KeywordRepository:

    @staticmethod
    async def get_keyword_by_id(keyword_id: UUID) -> Optional[Keyword]:
        """Retrieve a single Keyword by its UUID."""
        async with async_session() as session:
            statement = select(Keyword).where(Keyword.id == keyword_id)
            result = await session.execute(statement)
            return result.scalars().first()

    @staticmethod
    async def list_keywords(limit: int = 100, offset: int = 0) -> Sequence[Keyword]:
        """Retrieve a list of keywords with pagination."""
        async with async_session() as session:
            statement = (
                select(Keyword)
                .limit(limit)
                .offset(offset)
            )
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
            # 1) Keyword mitsamt vorhandener Artikel (eager) laden
            stmt = (
                select(Keyword)
                .options(selectinload(Keyword.articles))
                .where(Keyword.id == keyword_id)
            )
            result = await session.execute(stmt)
            keyword = result.scalars().first()

            if not keyword:
                raise ValueError(f"Keyword mit id {keyword_id} existiert nicht.")

            print(f"--> Adding {keyword.name}")

            # 2) Article laden
            stmt2 = select(Article).where(Article.id == article_id)
            result = await session.execute(stmt2)
            article = result.scalars().first()
            if not article:
                raise ValueError(f"Article mit id {article_id} existiert nicht.")

            # 3) Link-Objekt manuell erstellen und Score setzen
            link = ArticleKeywordLink(
                article_id=article_id,
                keyword_id=keyword_id,
                score=score
            )
            session.add(link)

            # 4) Commit und evtl. refresh, um die Relationships aktuell zu halten
            await session.commit()
            await session.refresh(keyword)

    @staticmethod
    async def get_most_similar_articles(
        keyword_id: UUID, score_threshold: float = 0.3
    ) -> Sequence[Article]:
        """Retrieve the most similar articles for a given keyword."""

        keyword = await KeywordRepository.get_keyword_by_id(keyword_id)
        if not keyword:
            return []
        articles = await article_vector_service.retrieve_by_similarity(keyword.name, score_threshold=score_threshold)

        result = []
        for article in articles:
            doc, score = article

            print(doc.metadata["id"])
            article_obj = await ArticleRepository.get_article_by_id(doc.metadata["id"])
            if article_obj:
                result.append(article_obj)

        return result

    @staticmethod
    async def assign_articles_to_keywords(page_size: int = 100) -> None:
        page = 0
        while True:
            offset = page * page_size

            keywords = await KeywordRepository.list_keywords(
                limit=page_size, offset=offset
            )
            print(f"Processing page {page} with {len(keywords)} keywords...")
            if not keywords:
                break

            for keyword in keywords:

                print(f"Processing keyword: {keyword.name}")
                similar_articles = await article_vector_service.retrieve_by_similarity(query=keyword.name, score_threshold=0.3)

                print("----------------------------------------")
                print(keyword)
                for similar_article in similar_articles:
                    doc, score = similar_article
                    print(f"Assigned article {doc.metadata['id']} to keyword {keyword.name}")
                    await KeywordRepository.add_article_to_keyword(keyword.id, doc.metadata["id"], score)
                    print(f"Assigned article {doc.metadata['id']} to keyword {keyword.name}")

            page += 1



