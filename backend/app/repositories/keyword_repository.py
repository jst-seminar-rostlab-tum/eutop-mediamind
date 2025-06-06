from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.db import async_session
from app.models import User
from app.models.keyword import Keyword
from app.models.topic import Topic
from app.schemas.keyword_schemas import KeywordCreateRequest


class KeywordsRepository:

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
            keywords = await session.execute(query)
            await session.commit()
            return keywords.rowcount > 0
