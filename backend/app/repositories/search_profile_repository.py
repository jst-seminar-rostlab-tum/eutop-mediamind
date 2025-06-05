from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.db import engine
from app.models import Topic, User
from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import (
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
    TopicResponse,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def save_search_profile(search_profile: SearchProfile) -> SearchProfile:
    async with async_session() as session:
        session.add(search_profile)
        await session.commit()
        await session.refresh(search_profile)
        return search_profile


async def get_available_search_profiles(
    current_user: User,
) -> list[SearchProfileDetailResponse]:
    accessible_search_profiles: list[SearchProfile] = (
        await get_accessible_profiles(
            current_user.id, current_user.organization_id
        )
    )

    available_search_profiles = []
    for search_profile in accessible_search_profiles:
        is_owner = search_profile.created_by_id == current_user.id
        is_editable = is_owner or current_user.is_superuser

        organization_emails = [
            user.email
            for user in search_profile.users
            if user.organization_id == current_user.organization_id
        ]
        profile_emails = [
            user.email
            for user in search_profile.users
            if user.organization_id != current_user.organization_id
        ]

        topic_responses = []
        for topic in search_profile.topics:
            keywords = [kw.name for kw in topic.keywords]
            topic_responses.append(
                TopicResponse(name=topic.name, keywords=keywords)
            )

        available_search_profiles.append(
            SearchProfileDetailResponse(
                id=search_profile.id,
                name=search_profile.name,
                organization_emails=organization_emails,
                profile_emails=profile_emails,
                public=search_profile.is_public,
                editable=is_editable,
                is_editable=is_editable,
                owner=search_profile.created_by_id,
                is_owner=is_owner,
                topics=topic_responses,
            )
        )

    return available_search_profiles


async def update_search_profile_by_id(
    search_profile_id: UUID, data: SearchProfileUpdateRequest
) -> Type[SearchProfile] | None:
    async with async_session() as session:
        search_profile = await session.get(SearchProfile, search_profile_id)
        if not search_profile:
            return None

        # Update simple fields
        search_profile.name = data.name
        search_profile.is_public = data.public
        search_profile.is_editable = data.is_editable
        search_profile.owner_id = data.owner
        search_profile.is_owner = data.is_owner

        # Update email lists
        if data.organization_emails is not None:
            search_profile.organization_emails = data.organization_emails

        if data.profile_emails is not None:
            search_profile.profile_emails = data.profile_emails

        # Update subscriptions (replace with new list)
        if data.subscriptions is not None:
            search_profile.subscriptions.clear()
            for sub_data in data.subscriptions:
                search_profile.subscriptions.append(sub_data.to_model())

        # Update topics (replace with new list)
        if data.topics is not None:
            search_profile.topics.clear()
            for topic_data in data.topics:
                search_profile.topics.append(topic_data.to_model())

        session.add(search_profile)
        await session.commit()
        await session.refresh(search_profile)

        return search_profile


async def get_accessible_profiles(user_id, organization_id):
    async with async_session() as session:
        accessible_profiles = await session.execute(
            select(SearchProfile)
            .options(
                selectinload(SearchProfile.users),
                selectinload(SearchProfile.topics).selectinload(
                    Topic.keywords
                ),
            )
            .where(
                SearchProfile.is_public
                | (SearchProfile.organization_id == organization_id)
                | (SearchProfile.users.any(User.id == user_id))
            )
        )
        return accessible_profiles.unique().scalars().all()


async def get_search_profile_by_id(
    search_profile_id: UUID, current_user: User
) -> SearchProfile | None:
    async with async_session() as session:
        search_profile = await session.execute(
            select(SearchProfile).where(SearchProfile.id == search_profile_id)
        )
        return search_profile.scalars().one_or_none()


async def save_updated_search_profile(
    search_profile: SearchProfile,
) -> SearchProfile:
    async with async_session() as session:
        session.add(search_profile)
        await session.commit()
        await session.refresh(search_profile)
        return search_profile
