from typing import List, Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.db import async_session
from app.models import Topic, User
from app.models.search_profile import SearchProfile
from app.repositories.subscription_repository import (
    set_subscriptions_for_profile,
)
from app.repositories.topics_repository import TopicsRepository
from app.schemas.search_profile_schemas import (
    SearchProfileCreateRequest,
    SearchProfileUpdateRequest,
)


async def create_profile_with_request(
    create_data: SearchProfileCreateRequest, current_user: User
) -> SearchProfile:
    async with async_session() as session:
        # Create and persist base profile
        profile = SearchProfile(
            name=create_data.name,
            is_public=create_data.is_public,
            organization_id=current_user.organization_id,
            created_by_id=create_data.owner_id,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        # Add related data: topics
        await TopicsRepository.update_topics(profile, create_data.topics)

        # Add subscriptions
        await set_subscriptions_for_profile(
            profile_id=profile.id, subscriptions=create_data.subscriptions
        )

        # Add emails
        await update_emails(
            profile,
            create_data.organization_emails,
            create_data.profile_emails,
        )

        # Refresh with eager-loaded relationships
        result = await session.execute(
            select(SearchProfile)
            .where(SearchProfile.id == profile.id)
            .options(
                selectinload(SearchProfile.users),
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            )
        )
        profile = result.scalars().one()
        return profile


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
    profile.organization_emails = [str(email) for email in organization_emails]
    profile.profile_emails = [str(email) for email in profile_emails]


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
