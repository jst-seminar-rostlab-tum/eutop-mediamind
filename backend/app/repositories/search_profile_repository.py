from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.db import async_session
from app.models import Topic, User
from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest


async def save_search_profile(search_profile: SearchProfile) -> SearchProfile:
    async with async_session() as session:
        session.add(search_profile)
        await session.commit()
        await session.refresh(search_profile)
        return search_profile


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


async def update_search_profile_by_id(
    search_profile_id: UUID, data: SearchProfileUpdateRequest
) -> SearchProfile | None:
    async with async_session() as session:
        search_profile = await session.get(SearchProfile, search_profile_id)
        if not search_profile:
            return None

        profile_update = data.model_dump(
            exclude_unset=True, exclude={"subscriptions", "topics"}
        )

        for field, value in profile_update.items():
            setattr(search_profile, field, value)

        if data.subscriptions is not None:
            search_profile.subscriptions.clear()
            search_profile.subscriptions.extend(
                sub.to_model() for sub in data.subscriptions
            )

        if data.topics is not None:
            search_profile.topics.clear()
            search_profile.topics.extend(
                topic.to_model() for topic in data.topics
            )

        session.add(search_profile)
        await session.commit()
        await session.refresh(search_profile)
        return search_profile
