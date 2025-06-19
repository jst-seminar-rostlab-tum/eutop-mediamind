from typing import List, Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import async_session
from app.models import Topic, User
from app.models.search_profile import SearchProfile
from app.repositories.subscription_repository import (
    set_subscriptions_for_profile,
)
from app.repositories.topics_repository import TopicsRepository
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest


async def create_profile_with_request(
    create_data,  # SearchProfileCreateRequest
    current_user,  # User
    session: AsyncSession,
) -> SearchProfile:
    # Persist base profile and get its ID
    profile = await _create_and_flush_profile(
        create_data, current_user, session
    )

    # Assign topics (in-session, no separate commit)
    await _assign_topics(profile.id, create_data.topics, session)

    # Assign subscriptions
    await set_subscriptions_for_profile(
        profile_id=profile.id,
        subscriptions=create_data.subscriptions,
        session=session,
    )

    # Load and return full profile with all relations
    return await _load_full_profile(profile.id, session)


async def _create_and_flush_profile(
    create_data, current_user, session: AsyncSession
) -> SearchProfile:
    profile = SearchProfile(
        name=create_data.name,
        is_public=create_data.is_public,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        owner_id=create_data.owner_id,
        language=create_data.language,
    )
    await update_emails(
        profile, create_data.organization_emails, create_data.profile_emails
    )
    session.add(profile)
    await session.flush()  # assign profile.id
    return profile


async def _load_full_profile(
    profile_id: str,
    session: AsyncSession,
) -> SearchProfile:
    result = await session.execute(
        select(SearchProfile)
        .where(SearchProfile.id == profile_id)
        .options(
            selectinload(SearchProfile.topics).selectinload(Topic.keywords),
            selectinload(SearchProfile.subscriptions),
            selectinload(SearchProfile.users),
        )
    )
    return result.scalar_one()


async def _assign_topics(
    profile_id: str,
    topics: List[TopicCreateOrUpdateRequest],
    session: AsyncSession,
) -> None:
    await TopicsRepository.update_topics(profile_id, topics, session)


async def get_accessible_profiles(
    user_id: UUID, organization_id: UUID
) -> list[SearchProfile]:
    async with async_session() as session:
        query = (
            select(SearchProfile)
            .distinct()
            .options(
                selectinload(SearchProfile.users),
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            )
            .where(
                or_(
                    SearchProfile.created_by_id == user_id,
                    SearchProfile.users.any(User.id == user_id),
                    and_(
                        SearchProfile.organization_id == organization_id,
                        SearchProfile.is_public,
                    ),
                )
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().all()


async def get_accessible_profile_by_id(
    search_profile_id: UUID, user_id: UUID, organization_id: UUID, session
) -> SearchProfile | None:
    query = (
        select(SearchProfile)
        .options(
            selectinload(SearchProfile.users),
            selectinload(SearchProfile.topics).selectinload(
                SearchProfile.topics.property.mapper.class_.keywords
            ),
        )
        .where(
            SearchProfile.id == search_profile_id,
            or_(
                SearchProfile.created_by_id == user_id,
                SearchProfile.users.any(User.id == user_id),
                and_(
                    SearchProfile.organization_id == organization_id,
                    SearchProfile.is_public,
                ),
            ),
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_search_profile_by_id(
    search_profile_id: UUID, current_user: User
) -> SearchProfile | None:
    async with async_session() as session:
        result = await session.execute(
            select(SearchProfile)
            .where(SearchProfile.id == search_profile_id)
            .options(
                selectinload(SearchProfile.users),
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            )
        )
        return result.scalars().one_or_none()


async def update_profile_with_request(
    profile: SearchProfile,
    update_data: SearchProfileUpdateRequest,
    user: User,
    session,
):
    # Update base fields
    profile.name = update_data.name
    profile.is_public = update_data.is_public
    profile.language = update_data.language

    # update owner of
    if user.id == profile.created_by_id or user.is_superuser:
        profile.created_by_id = update_data.owner_id

    await set_subscriptions_for_profile(
        profile_id=profile.id,
        subscriptions=update_data.subscriptions,
        session=session,
    )

    await TopicsRepository.update_topics(
        profile=profile,
        new_topics=update_data.topics,
        session=session,
    )

    await update_emails(
        profile,
        update_data.organization_emails,
        update_data.profile_emails,
    )

    session.add(profile)
    await session.commit()
    await session.refresh(profile)


async def update_emails(
    profile: SearchProfile,
    organization_emails: List[EmailStr],
    profile_emails: List[EmailStr],
) -> None:
    # Convert EmailStr to plain strings for storage in DB
    profile.organization_emails = (
        [str(email) for email in organization_emails]
        if organization_emails is not None
        else []
    )
    profile.profile_emails = (
        [str(email) for email in profile_emails]
        if profile_emails is not None
        else []
    )


class SearchProfileRepository:
    @staticmethod
    async def fetch_all_search_profiles(limit: int, offset: int):
        """
        Fetch all search profiles with pagination.
        """
        async with async_session() as session:
            query = select(SearchProfile).offset(offset).limit(limit)
            search_profiles: Sequence[SearchProfile] = (
                (await session.execute(query)).scalars().all()
            )
            return search_profiles
