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

        async with async_session() as session:
            result = await session.execute(
                delete(Topic).where(Topic.id == topic_id)
            )
            await session.commit()
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
        profile_id: UUID,
        new_topics: list[TopicCreateOrUpdateRequest],
        session: AsyncSession,
    ) -> None:
        # a) Profil mit Topics+Keywords laden
        profile = await session.get(
            SearchProfile,
            profile_id,
            options=[
                selectinload(SearchProfile.topics).selectinload(Topic.keywords)
            ],
        )

        new_names = {t.name for t in new_topics}

        # b) Entfernte Topics+Links löschen
        for old in profile.topics:
            if old.name not in new_names:
                await session.execute(
                    delete(TopicKeywordLink).where(
                        TopicKeywordLink.topic_id == old.id
                    )
                )
                session.delete(old)
        await session.flush()

        # c) Aktuelle Topics map
        profile = await session.get(
            SearchProfile,
            profile_id,
            options=[
                selectinload(SearchProfile.topics).selectinload(Topic.keywords)
            ],
        )
        existing = {t.name: t for t in profile.topics}

        # d) Alle Keywords vorladen
        rows = await session.execute(select(Keyword))
        kw_map = {k.name: k for k in rows.scalars().all()}

        # e) Neue/Update Topics + Keywords + Links
        for td in new_topics:
            topic = existing.get(td.name)
            if topic:
                # alte Links löschen
                await session.execute(
                    delete(TopicKeywordLink).where(
                        TopicKeywordLink.topic_id == topic.id
                    )
                )
            else:
                topic = Topic(name=td.name, search_profile_id=profile_id)
                session.add(topic)
                await session.flush()

            for name in td.keywords:
                kw = kw_map.get(name)
                if not kw:
                    kw = Keyword(name=name)
                    session.add(kw)
                    await session.flush()
                    kw_map[name] = kw

                session.add(
                    TopicKeywordLink(topic_id=topic.id, keyword_id=kw.id)
                )

        await session.flush()


async def _load_profile_with_topics(
    profile_id: str,
    session: AsyncSession,
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
    profile: SearchProfile,
    new_names: set[str],
    session: AsyncSession,
) -> None:
    for topic in profile.topics:
        if topic.name not in new_names:
            # remove links then topic
            await session.execute(
                delete(TopicKeywordLink).where(
                    TopicKeywordLink.topic_id == topic.id
                )
            )
            session.delete(topic)
    await session.flush()


async def _load_keywords_map(
    session: AsyncSession,
) -> dict[str, Keyword]:
    result = await session.execute(select(Keyword))
    return {k.name: k for k in result.scalars().all()}


async def _upsert_topics_and_keywords(
    profile_id: str,
    new_topics: List[TopicCreateOrUpdateRequest],
    keywords_map: dict[str, Keyword],
    session: AsyncSession,
) -> None:
    # reload profile to get fresh topics list
    profile = await _load_profile_with_topics(profile_id, session)
    existing = {t.name: t for t in profile.topics}

    for td in new_topics:
        topic = existing.get(td.name)
        if topic:
            # remove old links
            await session.execute(
                delete(TopicKeywordLink).where(
                    TopicKeywordLink.topic_id == topic.id
                )
            )
        else:
            topic = Topic(name=td.name, search_profile_id=profile_id)
            session.add(topic)
            await session.flush()

        # upsert keywords and links
        for kw_name in td.keywords:
            kw = keywords_map.get(kw_name)
            if not kw:
                kw = Keyword(name=kw_name)
                session.add(kw)
                await session.flush()
                keywords_map[kw_name] = kw

            link = TopicKeywordLink(topic_id=topic.id, keyword_id=kw.id)
            session.add(link)
    await session.flush()
