from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import async_session
from app.models import SearchProfile
from app.models.user import UserRole
from app.repositories.search_profile.filters import (
    base_load_options,
    user_access_filter,
)
from app.repositories.search_profile.updaters import (
    update_base_fields,
    update_emails,
    update_subscriptions,
    update_topics,
    update_user_rights,
)
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest


class SearchProfileRepository:
    """
    Repository for SearchProfile CRUD with access filters,
    eager loading, and update helpers.
    """

    @staticmethod
    async def get_accessible_profiles(
        user_id: UUID,
        organization_id: UUID,
        role: UserRole,
        is_superuser: bool,
    ) -> List[SearchProfile]:
        async with async_session() as session:
            query = (
                select(SearchProfile)
                .distinct()
                .options(*base_load_options())
                .where(
                    user_access_filter(
                        str(user_id),
                        str(organization_id),
                        role,
                        is_superuser,
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
        session: AsyncSession,
    ) -> Optional[SearchProfile]:
        query = (
            select(SearchProfile)
            .options(*base_load_options())
            .where(
                SearchProfile.id == search_profile_id,
                user_access_filter(
                    str(user_id),
                    str(organization_id),
                    user_role,
                    is_superuser,
                ),
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(
        profile: SearchProfile,
        data: SearchProfileUpdateRequest,
        current_user_id: UUID,
        is_superuser: bool,
        session: AsyncSession,
    ) -> SearchProfile:
        update_base_fields(
            profile,
            data.name,
            data.is_public,
            data.language,
            data.owner_id,
            current_user_id,
            is_superuser,
        )
        await update_subscriptions(
            profile_id=profile.id,
            subscriptions=data.subscriptions,
            session=session,
        )
        await update_topics(
            profile=profile,
            topics=data.topics,
            session=session,
        )
        update_emails(
            profile=profile,
            organization_emails=data.organization_emails,
            profile_emails=data.profile_emails,
        )
        update_user_rights(
            profile=profile,
            can_read_user_ids=data.can_read_user_ids,
            can_edit_user_ids=data.can_edit_user_ids,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def fetch_all_search_profiles(
        limit: int = None,
        offset: int = None,
    ) -> List[SearchProfile]:
        async with async_session() as session:
            query = select(SearchProfile)
            if offset is not None and limit is not None:
                query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()

    @staticmethod
    async def get_search_profile_by_id(
        search_profile_id: UUID,
    ) -> Optional[SearchProfile]:
        async with async_session() as session:
            query = (
                select(SearchProfile)
                .where(SearchProfile.id == search_profile_id)
                .options(*base_load_options())
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

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
        profile_id: UUID,
        can_read_user_ids: List[UUID],
        can_edit_user_ids: List[UUID],
        session: AsyncSession,
    ) -> None:
        from sqlalchemy import update

        stmt = (
            update(SearchProfile)
            .where(SearchProfile.id == profile_id)
            .values(
                can_read_user_ids=[str(uid) for uid in can_read_user_ids],
                can_edit_user_ids=[str(uid) for uid in can_edit_user_ids],
            )
        )
        await session.execute(stmt)
        await session.flush()

    @staticmethod
    async def delete_by_id(
        session: AsyncSession,
        profile_id: UUID,
    ) -> None:
        from sqlalchemy import delete

        stmt = delete(SearchProfile).where(SearchProfile.id == profile_id)
        await session.execute(stmt)
