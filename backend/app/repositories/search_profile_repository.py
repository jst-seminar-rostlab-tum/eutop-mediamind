from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.db import async_session
from app.models import SearchProfile, Topic, User
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest
from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest
from app.schemas.user_schema import UserEntity


def _public_or_user_filter(user_id: UUID, organization_id: UUID):
    return or_(
        SearchProfile.created_by_id == user_id,
        SearchProfile.users.any(User.id == user_id),
        and_(
            SearchProfile.organization_id == organization_id,
            SearchProfile.is_public,
        ),
    )


def _base_load_options():
    return [
        selectinload(SearchProfile.users),
        selectinload(SearchProfile.topics).selectinload(Topic.keywords),
    ]


def _update_base_fields(
    profile: SearchProfile,
    data: SearchProfileUpdateRequest,
    user: UserEntity,
):
    profile.name = data.name
    profile.is_public = data.is_public
    profile.language = data.language
    if user.id == profile.created_by_id or user.is_superuser:
        profile.created_by_id = data.owner_id


async def _update_subscriptions(
    profile_id: UUID,
    subscriptions: List[SubscriptionSummary],
    session,
):
    await SubscriptionRepository.set_subscriptions_for_profile(
        profile_id=profile_id,
        subscriptions=subscriptions,
        session=session,
    )


async def _update_topics(
    profile: SearchProfile,
    topics: list[TopicCreateOrUpdateRequest],
    session,
):
    await TopicsRepository.update_topics(
        profile=profile,
        new_topics=topics,
        session=session,
    )


def _update_emails(
    profile: SearchProfile,
    organization_emails: Optional[List[EmailStr]],
    profile_emails: Optional[List[EmailStr]],
):
    profile.organization_emails = (
        [str(e) for e in organization_emails] if organization_emails else []
    )
    profile.profile_emails = (
        [str(e) for e in profile_emails] if profile_emails else []
    )


def _update_user_rights(
    profile: SearchProfile,
    can_read: Optional[List[UUID]],
    can_edit: Optional[List[UUID]],
):
    profile.can_read = [str(e) for e in can_read] if can_read else []
    profile.can_edit = [str(e) for e in can_edit] if can_edit else []


class SearchProfileRepository:
    """
    Repository for CRUD operations on SearchProfile with clear separation
    of query construction, update logic, and session management.
    """

    @staticmethod
    async def get_accessible_profiles(
        user_id: UUID, organization_id: UUID
    ) -> List[SearchProfile]:
        """
        Return all profiles that the user can access
        (created, subscribed, or public).
        """
        async with async_session() as session:
            query = (
                select(SearchProfile)
                .distinct()
                .options(*_base_load_options())
                .where(_public_or_user_filter(user_id, organization_id))
            )
            result = await session.execute(query)
            return result.unique().scalars().all()

    @staticmethod
    async def get_accessible_profile_by_id(
        search_profile_id: UUID,
        user_id: UUID,
        organization_id: UUID,
        session,
    ) -> Optional[SearchProfile]:
        """
        Return a single profile by ID if accessible to the user.
        """
        query = (
            select(SearchProfile)
            .options(*_base_load_options())
            .where(
                SearchProfile.id == search_profile_id,
                _public_or_user_filter(user_id, organization_id),
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(
        profile: SearchProfile,
        data: SearchProfileUpdateRequest,
        current_user: UserEntity,
        session,
    ) -> SearchProfile:
        """
        Apply changes from request to the profile, including
        base fields, subscriptions, topics, and emails.
        """
        _update_base_fields(profile, data, current_user)
        await _update_subscriptions(profile.id, data.subscriptions, session)
        await _update_topics(profile, data.topics, session)
        _update_emails(
            profile=profile,
            organization_emails=data.organization_emails or [],
            profile_emails=data.profile_emails or [],
        )
        _update_user_rights(
            profile=profile,
            can_read=data.can_read or [],
            can_edit=data.can_edit or [],
        )

        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def fetch_all_search_profiles(
        limit: int, offset: int
    ) -> List[SearchProfile]:
        """
        Fetch all search profiles with pagination.
        """
        async with async_session() as session:
            query = select(SearchProfile).offset(offset).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_search_profile_by_id(
        search_profile_id: UUID,
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

    @staticmethod
    async def get_by_id(
        search_profile_id: UUID,
    ) -> Optional[SearchProfile]:
        async with async_session() as session:
            result = await session.execute(
                select(SearchProfile).where(
                    SearchProfile.id == search_profile_id
                )
            )
            return result.scalars().one_or_none()

    @staticmethod
    async def update_user_rights(
        profile: SearchProfile,
        can_read: List[UUID],
        can_edit: List[UUID],
        session: AsyncSession,
    ) -> None:
        # bulk‐update the two list-columns in one go
        await session.execute(
            update(SearchProfile)
            .where(SearchProfile.id == profile.id)
            .values(
                can_edit=can_edit,
                can_read=can_read,
            )
        )
        await session.flush()
