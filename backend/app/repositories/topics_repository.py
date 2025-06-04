from uuid import UUID

from sqlalchemy import delete, select

from app.core.db import async_session
from app.models.search_profile import SearchProfile
from app.models.topic import Topic
from app.schemas.topic_schemas import TopicCreateRequest


class TopicsRepository:
    @staticmethod
    async def get_topics_by_profile(profile_id: UUID, user):
        async with async_session() as session:
            query = (
                select(Topic)
                .join(SearchProfile)
                .where(
                    SearchProfile.id == profile_id,
                    SearchProfile.user_id == user.id,
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add_topic(profile_id: UUID, request: TopicCreateRequest, user):
        async with async_session() as session:
            topic = Topic(name=request.name, search_profile_id=profile_id)
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

    @staticmethod
    async def delete_topic(profile_id: UUID, topic_id: UUID, user):
        async with async_session() as session:
            query = delete(Topic).where(
                Topic.id == topic_id,
                Topic.search_profile_id == profile_id,
                Topic.search_profile.has(user_id=user.id),
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0