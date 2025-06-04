from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, select

from app.core.db import engine
from app.models import Topic, User
from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import (
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
    TopicResponse,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def save_search_profile(profile: SearchProfile) -> SearchProfile:
    async with async_session() as session:
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile


async def get_by_id(
    search_profile_id: UUID, current_user
) -> SearchProfileDetailResponse | None:
    user_id = current_user.id
    organization_id = current_user.organization_id

    async with async_session() as session:
        stmt = select(SearchProfile).options(selectinload(SearchProfile.users))

        base_condition = SearchProfile.id == search_profile_id

        access_conditions = [
            SearchProfile.is_public,
            SearchProfile.users.any(id=user_id),
        ]

        if organization_id is not None:
            access_conditions.append(
                SearchProfile.organization_id == organization_id
            )

        stmt = stmt.where(and_(base_condition, or_(*access_conditions)))

        result = await session.execute(stmt)
        return result.one_or_none()


async def get_available_search_profiles(
    current_user: User,
) -> list[SearchProfileDetailResponse]:
    profiles: list[SearchProfile] = await get_accessible_profiles(
        current_user.id, current_user.organization_id
    )

    response_profiles = []
    for profile in profiles:
        is_owner = profile.created_by_id == current_user.id
        is_editable = is_owner or current_user.is_superuser

        organization_emails = [
            user.email
            for user in profile.users
            if user.organization_id == current_user.organization_id
        ]
        profile_emails = [
            user.email
            for user in profile.users
            if user.organization_id != current_user.organization_id
        ]

        topic_responses = []
        for topic in profile.topics:
            keywords = [kw.name for kw in topic.keywords]
            topic_responses.append(
                TopicResponse(name=topic.name, keywords=keywords)
            )

        response_profiles.append(
            SearchProfileDetailResponse(
                id=profile.id,
                name=profile.name,
                organization_emails=organization_emails,
                profile_emails=profile_emails,
                public=profile.is_public,
                editable=is_editable,
                is_editable=is_editable,
                owner=profile.created_by_id,
                is_owner=is_owner,
                topics=topic_responses,
            )
        )

    return response_profiles


async def update_by_id(
    profile_id: UUID, data: SearchProfileUpdateRequest
) -> Type[SearchProfile] | None:
    async with async_session() as session:
        profile = await session.get(SearchProfile, profile_id)
        if not profile:
            return None

        # Update simple fields
        profile.name = data.name
        profile.is_public = data.public
        profile.is_editable = data.is_editable
        profile.owner_id = data.owner
        profile.is_owner = data.is_owner

        # Update email lists
        if data.organization_emails is not None:
            profile.organization_emails = data.organization_emails

        if data.profile_emails is not None:
            profile.profile_emails = data.profile_emails

        # Update subscriptions (replace with new list)
        if data.subscriptions is not None:
            profile.subscriptions.clear()
            for sub_data in data.subscriptions:
                profile.subscriptions.append(sub_data.to_model())

        # Update topics (replace with new list)
        if data.topics is not None:
            profile.topics.clear()
            for topic_data in data.topics:
                profile.topics.append(topic_data.to_model())

        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        return profile


async def get_accessible_profiles(user_id, organization_id):
    async with async_session() as session:
        result = await session.execute(
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
        return result.unique().scalars().all()


async def get_by_id_raw(
    profile_id: UUID, current_user: User
) -> SearchProfile | None:
    async with async_session() as session:
        result = await session.execute(
            select(SearchProfile).where(SearchProfile.id == profile_id)
        )
        return result.scalars().one_or_none()


async def save_updated_search_profile(profile: SearchProfile) -> SearchProfile:
    async with async_session() as session:
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile
