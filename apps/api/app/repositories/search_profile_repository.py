from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import and_, delete, or_, true, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.db import async_session
from app.models import SearchProfile, Topic, User
from app.models.user import UserRole
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest
from app.schemas.subscription_schemas import SubscriptionSummary
from app.schemas.topic_schemas import TopicCreateOrUpdateRequest
from app.schemas.user_schema import UserEntity


def _user_access_filter(
    user_id: UUID, organization_id: UUID, role: UserRole, is_superuser: bool
):
    if is_superuser:
        return true()  # SQLAlchemy "always true" condition

    if role == UserRole.maintainer:
        return SearchProfile.organization_id == organization_id

    # default: owned, subscribed, public in org
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
    can_read_user_ids: Optional[List[UUID]],
    can_edit_user_ids: Optional[List[UUID]],
):
    profile.can_read_user_ids = (
        [str(user_id) for user_id in can_read_user_ids]
        if can_read_user_ids
        else []
    )
    profile.can_edit_user_ids = (
        [str(user_id) for user_id in can_edit_user_ids]
        if can_edit_user_ids
        else []
    )


class SearchProfileRepository:
    """
    Repository for CRUD operations on SearchProfile with clear separation
    of query construction, update logic, and session management.
    """

    @staticmethod
    async def get_accessible_profiles(
        user_id: UUID,
        organization_id: UUID,
        role: UserRole,
        is_superuser: bool,
    ) -> List[SearchProfile]:
        """
        Return all profiles that the user can access:
        - owned or subscribed
        - public in org
        - if superuser: all
        - if maintainer: all in org
        """
        async with async_session() as session:
            query = (
                select(SearchProfile)
                .distinct()
                .options(*_base_load_options())
                .where(
                    _user_access_filter(
                        user_id, organization_id, role, is_superuser
                    )
                )
            )
            result = await session.execute(query)
            return result.unique().scalars().all()

    @staticmethod
    async def get_accessible_profile_by_id(
        search_profile_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        is_superuser: bool,
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
                _user_access_filter(
                    user_id, organization_id, user_role, is_superuser
                ),
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
            can_read_user_ids=data.can_read_user_ids or [],
            can_edit_user_ids=data.can_edit_user_ids or [],
        )

        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def fetch_all_search_profiles(
        limit: int = None, offset: int = None
    ) -> List[SearchProfile]:
        """
        Fetch all search profiles with pagination.
        """
        async with async_session() as session:
            query = select(SearchProfile).options(
                selectinload(SearchProfile.organization)
            )
            if offset is not None and limit is not None:
                query = query.offset(offset).limit(limit)

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
        can_read_user_ids: List[UUID],
        can_edit_user_ids: List[UUID],
        session: AsyncSession,
    ) -> None:
        # bulk‐update the two list-columns in one go
        await session.execute(
            update(SearchProfile)
            .where(SearchProfile.id == profile.id)
            .values(
                can_edit_user_ids=can_edit_user_ids,
                can_read_user_ids=can_read_user_ids,
            )
        )
        await session.flush()

    @staticmethod
    async def delete_by_id(session: AsyncSession, profile_id: UUID) -> None:
        stmt = delete(SearchProfile).where(SearchProfile.id == profile_id)
        await session.execute(stmt)
