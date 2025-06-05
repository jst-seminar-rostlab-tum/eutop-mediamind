from uuid import UUID

from sqlalchemy import delete, select

from app.core.db import async_session
from app.models.search_profile import SearchProfile
from app.models.topic import Topic
from app.schemas.topic_schemas import TopicCreateRequest


class TopicsRepository:
    @staticmethod
    async def get_topics_by_search_profile(search_profile_id: UUID, user):
        async with async_session() as session:
            query = (
                select(Topic)
                .join(SearchProfile)
                .where(
                    SearchProfile.id == search_profile_id,
                    SearchProfile.user_id == user.id,
                )
            )
            topics = await session.execute(query)
            return topics.scalars().all()

    @staticmethod
    async def add_topic(
        search_profile_id: UUID, request: TopicCreateRequest, user
    ):
        async with async_session() as session:
            topic = Topic(
                name=request.name, search_profile_id=search_profile_id
            )
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

    @staticmethod
    async def delete_topic(search_profile_id: UUID, topic_id: UUID, user):
        async with async_session() as session:
            query = delete(Topic).where(
                Topic.id == topic_id,
                Topic.search_profile_id == search_profile_id,
                Topic.search_profile.has(user_id=user.id),
            )
            topics = await session.execute(query)
            await session.commit()
            return topics.rowcount > 0
