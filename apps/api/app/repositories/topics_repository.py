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
    async def get_topic_names_by_ids(topic_ids: set[UUID]) -> dict[UUID, str]:
        async with async_session() as session:
            result = await session.execute(
                select(Topic.id, Topic.name).where(Topic.id.in_(topic_ids))
            )
            return {row.id: row.name for row in result.all()}

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
        # 1) load the profile WITH its topics collection
        profile = await _load_profile_with_topics(session, profile.id)

        # 2) build a name→Topic map of the existing (pre-edit) topics
        old_topics = {t.name: t for t in profile.topics}
        new_names = {t.name for t in new_topics}

        # 3) delete (and remove) any orphaned topics
        for name in list(old_topics.keys()):
            if name not in new_names:
                topic = old_topics.pop(name)
                # mark it for deletion in the DB
                await session.delete(topic)
                # *also* remove it from the in-memory relationship
                profile.topics.remove(topic)

        # 4) make sure we have every keyword in memory
        all_keywords = await _preload_all_keywords(session)

        # 5) insert or update the remaining topics & their links
        for tdata in new_topics:
            topic = old_topics.get(tdata.name)
            if not topic:
                # brand-new Topic
                topic = Topic(name=tdata.name, search_profile_id=profile.id)
                session.add(topic)
                await session.flush()
                # and attach it to the profile
                profile.topics.append(topic)

            # clear all the old links for this topic
            await session.execute(
                delete(TopicKeywordLink).where(
                    TopicKeywordLink.topic_id == topic.id
                )
            )

            # re-add links for the new keyword set
            for kw_name in tdata.keywords:
                kw = all_keywords.get(kw_name)
                if not kw:
                    kw = Keyword(name=kw_name)
                    session.add(kw)
                    await session.flush()
                    all_keywords[kw_name] = kw

                session.add(
                    TopicKeywordLink(
                        topic_id=topic.id,
                        keyword_id=kw.id,
                    )
                )

        await session.flush()
        
        # 6) delete orphaned keywords that have no more topic links
        await _delete_orphaned_keywords(session)
        
        await session.refresh(profile, ["topics"])

    @staticmethod
    async def delete_keyword_links_for_search_profile(
        session: AsyncSession, topic_ids: List[UUID]
    ) -> None:
        """
        Delete all entries in the linking table for keywords of topics
        associated with the given search profile.
        """
        if not topic_ids:
            return
        # Cast to tuple for better type inference
        ids_tuple = tuple(topic_ids)
        stmt = delete(TopicKeywordLink).where(
            TopicKeywordLink.topic_id.in_(ids_tuple)
        )
        await session.execute(stmt)

    @staticmethod
    async def delete_for_search_profile(
        session: AsyncSession, profile_id: UUID
    ) -> None:
        stmt = delete(Topic).where(Topic.search_profile_id == profile_id)
        await session.execute(stmt)


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


async def _delete_orphaned_keywords(session: AsyncSession) -> None:
    """
    Delete keywords that have no TopicKeywordLink associations.
    """
    # Find keywords that have no topic links
    orphaned_keywords_query = (
        select(Keyword)
        .outerjoin(TopicKeywordLink, Keyword.id == TopicKeywordLink.keyword_id)
        .where(TopicKeywordLink.keyword_id.is_(None))
    )

    orphaned_keywords = await session.scalars(orphaned_keywords_query)

    for keyword in orphaned_keywords.all():
        await session.delete(keyword)


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
