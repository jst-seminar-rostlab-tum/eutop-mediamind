from uuid import UUID

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
            is_public=create_data.public,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        # Add related data: topics
        await TopicsRepository.update_topics(profile, create_data.topics)

        # Add subscriptions
        subscription_ids = [s.id for s in create_data.subscriptions]
        await set_subscriptions_for_profile(
            profile_id=profile.id, subscription_ids=subscription_ids
        )

        # Add emails
        # await update_emails(profile, update_data.organization_emails,
        # update_data.profile_emails, session)

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
):
    async with async_session() as session:
        # Update base fields
        profile.name = update_data.name
        profile.is_public = update_data.public

        await set_subscriptions_for_profile(
            profile_id=profile.id,
            subscription_ids=[s.id for s in update_data.subscriptions],
        )

        await TopicsRepository.update_topics(profile, update_data.topics)
        # await update_emails(profile, update_data.organization_emails,
        # update_data.profile_emails, session)

        session.add(profile)
        await session.commit()
        await session.refresh(profile)
