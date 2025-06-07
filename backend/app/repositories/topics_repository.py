from uuid import UUID

from sqlalchemy import delete, select

from app.core.db import async_session
from app.models import Keyword, SearchProfile, Topic
from app.models.associations import TopicKeywordLink
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest


class TopicsRepository:
    @staticmethod
    async def get_topics_by_search_profile(
        search_profile_id: UUID, user
    ) -> list[Topic]:
        async with async_session() as session:
            query = (
                select(Topic)
                .join(SearchProfile)
                .where(
                    SearchProfile.id == search_profile_id,
                    SearchProfile.created_by_id == user.id,
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add_topic(
        search_profile_id: UUID, request: TopicCreateOrUpdateRequest, user
    ) -> Topic:
        async with async_session() as session:
            topic = Topic(
                name=request.name, search_profile_id=search_profile_id
            )
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

    @staticmethod
    async def delete_topic(
        search_profile_id: UUID, topic_id: UUID, user
    ) -> bool:
        async with async_session() as session:
            result = await session.execute(
                delete(Topic).where(
                    Topic.id == topic_id,
                    Topic.search_profile_id == search_profile_id,
                    Topic.search_profile.has(created_by_id=user.id),
                )
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def update_topics(
        profile: SearchProfile,
        new_topics: list[TopicCreateOrUpdateRequest],
    ):
        async with async_session() as session:
            # Delete existing topics and keyword links
            for topic in profile.topics:
                await session.execute(
                    delete(TopicKeywordLink).where(
                        TopicKeywordLink.topic_id == topic.id
                    )
                )
                await session.delete(topic)
            await session.commit()

            # Create new topics and their keywords
            for topic_data in new_topics:
                topic = Topic(
                    name=topic_data.name, search_profile_id=profile.id
                )
                session.add(topic)
                await session.flush()

                for keyword_name in topic_data.keywords:
                    keyword = Keyword(name=keyword_name)
                    session.add(keyword)
                    await session.flush()

                    link = TopicKeywordLink(
                        topic_id=topic.id, keyword_id=keyword.id
                    )
                    session.add(link)

            await session.commit()
