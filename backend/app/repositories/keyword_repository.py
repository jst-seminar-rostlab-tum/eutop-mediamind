from typing import List, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models import Article, ArticleKeywordLink, Keyword, Topic, User
from app.models.associations import TopicKeywordLink
from app.repositories.article_repository import ArticleRepository
from app.schemas.keyword_schemas import KeywordCreateRequest
from app.services.article_vector_service import ArticleVectorService

logger = get_logger(__name__)


class KeywordRepository:
    """Unified repository for managing Keyword entities and relations."""

    __article_vector_service = ArticleVectorService()

    @staticmethod
    async def get_keyword_by_id(keyword_id: UUID) -> Optional[Keyword]:
        async with async_session() as session:
            statement = select(Keyword).where(Keyword.id == keyword_id)
            return (await session.execute(statement)).scalar_one_or_none()

    @staticmethod
    async def list_keywords(
        limit: int = 100, offset: int = 0
    ) -> Sequence[Keyword]:
        async with async_session() as session:
            result = await session.execute(
                select(Keyword).limit(limit).offset(offset)
            )
            return result.scalars().all()

    @staticmethod
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
    async def get_keywords_by_topic(
        topic_id: UUID, user: User
    ) -> list[Keyword]:
        async with async_session() as session:
            query = (
                select(Topic)
                .where(Topic.id == topic_id)
                .options(selectinload(Topic.keywords))
            )
            topic = (await session.execute(query)).scalar_one_or_none()
            if topic is None:
                raise HTTPException(status_code=404, detail="Topic not found")
            return topic.keywords

    @staticmethod
    async def create_keyword_by_topic(
        topic_id: UUID, keyword_name: str, user: User
    ):
        """
        Create a keyword by topic ID.
        (endpoint for demo day)
        """

        async with async_session() as session:
            topic = await session.get(Topic, topic_id)
            if topic is None:
                raise HTTPException(status_code=404, detail="Topic not found")

            keyword = Keyword(name=keyword_name)
            session.add(keyword)
            await session.flush()
            link_stmt = insert(TopicKeywordLink).values(
                topic_id=topic_id, keyword_id=keyword.id
            )
            await session.execute(link_stmt)
            await session.commit()
            await session.refresh(keyword)
            return keyword

    @staticmethod
    async def add_keyword(
        topic_id: UUID, request: KeywordCreateRequest, user: User
    ) -> Keyword:
        async with async_session() as session:
            topic = await session.get(
                Topic, topic_id, options=[joinedload(Topic.search_profile)]
            )
            if topic is None or topic.search_profile.user_id != user.id:
                raise HTTPException(status_code=403, detail="Not authorized")

            keyword = Keyword(value=request.value, topic_id=topic_id)
            session.add(keyword)
            await session.commit()
            await session.refresh(keyword)
            return keyword

    @staticmethod
    async def delete_keyword(
        topic_id: UUID, keyword_id: UUID, user: User
    ) -> bool:
        async with async_session() as session:
            query = delete(Keyword).where(
                Keyword.id == keyword_id,
                Keyword.topic_id == topic_id,
                Keyword.topic.has(search_profile__user_id=user.id),
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    # --- Article Linking ---

    @staticmethod
    async def add_article_to_keyword(
        keyword_id: UUID, article_id: UUID, score: float
    ) -> None:
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
        keyword = await KeywordRepository.get_keyword_by_id(keyword_id)
        if not keyword:
            raise ValueError(f"Keyword with id {keyword_id} not found.")

        similarity_results = await KeywordRepository.__article_vector_service.retrieve_by_similarity(  # noqa: E501
            keyword.name, score_threshold=score_threshold
        )

        similar_articles: List[Article] = []
        for doc, score in similarity_results:
            article_id = doc.metadata["id"]
            article = await ArticleRepository.get_article_by_id(article_id)
            if article:
                similar_articles.append(article)
            else:
                raise ValueError(f"Article with id {article_id} not found.")

        return similar_articles

    @staticmethod
    async def assign_articles_to_keywords(
        page_size: int = 100, score_threshold: float = 0.3
    ) -> None:
        page = 0
        keywords = await KeywordRepository.list_keywords(
            limit=page_size, offset=page * page_size
        )

        while keywords:
            logger.info(
                f"Processing keywords "
                f"from {page * page_size} to {(page + 1) * page_size}"
            )
            for keyword in keywords:
                similar_articles = await KeywordRepository.__article_vector_service.retrieve_by_similarity(  # noqa: E501
                    query=keyword.name, score_threshold=score_threshold
                )

                for doc, score in similar_articles:
                    await KeywordRepository.add_article_to_keyword(
                        keyword.id, doc.metadata["id"], score
                    )
                    logger.info(
                        f"Assigned article {doc.metadata['id']} to "
                        f"keyword {keyword.name} with score {score}"
                    )

            page += 1
            keywords = await KeywordRepository.list_keywords(
                limit=page_size, offset=page * page_size
            )
