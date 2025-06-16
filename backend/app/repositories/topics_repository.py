from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.core.logger import get_logger
from app.models import Keyword, SearchProfile, Topic, User
from app.models.associations import TopicKeywordLink
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest

logger = get_logger(__name__)


class TopicsRepository:
    """
    Repository for CRUD operations on Topic, with clear separation of concerns
    and no use of class methods.
    """

    @staticmethod
    async def get_topics_by_search_profile(
        search_profile_id: UUID, user: User
    ) -> List[Topic]:
        """
        Return topics for a given search profile if the user is the owner.
        """
        async with async_session() as session:
            query = _build_profile_topics_query(search_profile_id, user.id)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def add_topic(
        search_profile_id: UUID,
        request: TopicCreateOrUpdateRequest,
        user: User,
    ) -> Topic:
        """
        Create a new topic under a specific search profile.
        """
        async with async_session() as session:
            topic = Topic(
                name=request.name, search_profile_id=search_profile_id
            )
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            return topic

    @staticmethod
    async def delete_topic_by_id(topic_id: UUID, user: User) -> bool:
        """
        Delete a topic by its ID (demo endpoint).
        """
        async with async_session() as session:
            result = await session.execute(
                delete(Topic).where(Topic.id == topic_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_topic(
        search_profile_id: UUID,
        topic_id: UUID,
        user: User,
    ) -> bool:
        """
        Delete a topic if it belongs to the user's search profile.
        """
        async with async_session() as session:
            query = delete(Topic).where(
                Topic.id == topic_id,
                Topic.search_profile_id == search_profile_id,
                Topic.search_profile.has(created_by_id=user.id),
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def update_topics(
        profile: SearchProfile,
        new_topics: List[TopicCreateOrUpdateRequest],
        session: AsyncSession,
    ) -> None:
        """
        Sync DB topics & keyword links to match `new_topics` list.
        """
        profile_with_topics = await _load_profile_with_topics(
            session, profile.id
        )
        old_topics = {t.name: t for t in profile_with_topics.topics}
        new_names = {t.name for t in new_topics}

        await _delete_removed_topics(session, old_topics, new_names)
        all_keywords = await _preload_all_keywords(session)
        await _upsert_topics_and_links(
            session, profile.id, old_topics, new_topics, all_keywords
        )


# -- Helper functions (module-level) --


def _build_profile_topics_query(search_profile_id: UUID, user_id: UUID):
    return (
        select(Topic)
        .join(SearchProfile)
        .where(
            SearchProfile.id == search_profile_id,
            SearchProfile.created_by_id == user_id,
        )
    )


async def _load_profile_with_topics(
    session: AsyncSession, profile_id: UUID
) -> SearchProfile:
    result = await session.execute(
        select(SearchProfile)
        .where(SearchProfile.id == profile_id)
        .options(
            selectinload(SearchProfile.topics).selectinload(Topic.keywords)
        )
    )
    return result.scalar_one()


async def _delete_removed_topics(
    session: AsyncSession,
    old_topics: dict[str, Topic],
    new_names: set[str],
) -> None:
    for name, topic in old_topics.items():
        if name not in new_names:
            await session.execute(
                delete(TopicKeywordLink).where(
                    TopicKeywordLink.topic_id == topic.id
                )
            )
            await session.delete(topic)
    await session.flush()


async def _preload_all_keywords(
    session: AsyncSession,
) -> dict[str, Keyword]:
    kws = await session.scalars(select(Keyword))
    return {kw.name: kw for kw in kws.all()}


async def _upsert_topics_and_links(
    session: AsyncSession,
    profile_id: UUID,
    old_topics: dict[str, Topic],
    new_topics: List[TopicCreateOrUpdateRequest],
    all_keywords: dict[str, Keyword],
) -> None:
    for tdata in new_topics:
        topic = old_topics.get(tdata.name)
        if not topic:
            topic = Topic(name=tdata.name, search_profile_id=profile_id)
            session.add(topic)
            await session.flush()

        # clear existing links
        await session.execute(
            delete(TopicKeywordLink).where(
                TopicKeywordLink.topic_id == topic.id
            )
        )

        # add new links
        for kw_name in tdata.keywords:
            kw = all_keywords.get(kw_name)
            if not kw:
                kw = Keyword(name=kw_name)
                session.add(kw)
                await session.flush()
                all_keywords[kw_name] = kw

            session.add(TopicKeywordLink(topic_id=topic.id, keyword_id=kw.id))
    await session.flush()
