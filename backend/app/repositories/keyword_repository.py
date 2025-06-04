from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session
from app.models.keyword import Keyword
from app.models.topic import Topic
from app.schemas.keyword_schemas import KeywordCreateRequest

class KeywordsRepository:
    @staticmethod
    async def get_keywords_by_topic(topic_id: UUID, user):
        async with async_session() as session:
            query = select(Keyword).join(Topic).where(
                Keyword.topic_id == topic_id,
                Topic.id == topic_id,
                Topic.search_profile.has(user_id=user.id)
            )
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add_keyword(topic_id: UUID, request: KeywordCreateRequest, user):
        async with async_session() as session:
            keyword = Keyword(
                value=request.value,
                topic_id=topic_id
            )
            session.add(keyword)
            await session.commit()
            await session.refresh(keyword)
            return keyword

    @staticmethod
    async def delete_keyword(topic_id: UUID, keyword_id: UUID, user):
        async with async_session() as session:
            query = delete(Keyword).where(
                Keyword.id == keyword_id,
                Keyword.topic_id == topic_id,
                Keyword.topic.has(search_profile__user_id=user.id)
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0
