from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models import Keyword, SearchProfile, Topic, User
from app.models.associations import TopicKeywordLink
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest

logger = get_logger(__name__)


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
            topics = (await session.execute(query)).scalars().all()

            return topics

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
    async def create_topic_by_search_profile(
        search_profile_id: UUID, topic_name: str, user
    ) -> Topic:
        """
        Create a topic by search profile ID.
        (endpoint for demo day)
        """
        async with async_session() as session:
            """
            # Verify that the SearchProfile exists and
            # the user has access to it
            query = (
                select(SearchProfile)
                .where(SearchProfile.id == search_profile_id)
                .join(SearchProfile.users)
                .where(User.id == user.id)
            )

            search_profile = (await session.execute(query)).one_or_none()

            if not search_profile:
                raise ValueError("Search profile not found or access denied.")
            """

            topic = Topic(name=topic_name, search_profile_id=search_profile_id)
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

    @staticmethod
    async def delete_topic_by_id(topic_id: UUID, user: User) -> bool:
        """
        Delete a topic by ID, ensuring the user has permission
        (endpoint for demo day).
        """
        logger.info(f"Deleting topic {topic_id} for user {user.id}")
        async with async_session() as session:
            result = await session.execute(
                delete(Topic).where(Topic.id == topic_id)
            )
            await session.commit()
            print(result)
            return result.rowcount > 0

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
        session,
    ):
        profile = await session.get(
            SearchProfile,
            profile.id,
            options=[
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            ],
        )

        new_topic_names = {t.name for t in new_topics}

        # Step 1: Delete removed topics
        for existing_topic in profile.topics:
            if existing_topic.name not in new_topic_names:
                await session.execute(
                    delete(TopicKeywordLink).where(
                        TopicKeywordLink.topic_id == existing_topic.id
                    )
                )
                await session.delete(existing_topic)

        await session.commit()

        # SAFE: reload profile with topics and keywords
        profile = await session.get(
            SearchProfile,
            profile.id,
            options=[
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            ],
        )

        # Rebuild topic lookup with only the remaining topics
        existing_topic_map = {topic.name: topic for topic in profile.topics}

        # Preload keywords
        result = await session.execute(select(Keyword))
        existing_keywords: dict[str, Keyword] = {
            keyword.name: keyword for keyword in result.scalars().all()
        }

        # Step 2: Add or update topics
        for topic_data in new_topics:
            existing_topic = existing_topic_map.get(topic_data.name)

            if existing_topic:
                await session.execute(
                    delete(TopicKeywordLink).where(
                        TopicKeywordLink.topic_id == existing_topic.id
                    )
                )
                topic = existing_topic
            else:
                topic = Topic(
                    name=topic_data.name,
                    search_profile_id=profile.id,
                )
                session.add(topic)
                await session.flush()

            for keyword_name in topic_data.keywords:
                keyword = existing_keywords.get(keyword_name)
                if not keyword:
                    keyword = Keyword(name=keyword_name)
                    session.add(keyword)
                    await session.flush()
                    existing_keywords[keyword_name] = keyword

                session.add(
                    TopicKeywordLink(topic_id=topic.id, keyword_id=keyword.id)
                )

        await session.commit()
