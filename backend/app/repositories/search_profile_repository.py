from typing import Type, Tuple
from uuid import UUID

from sqlalchemy.orm import selectinload, joinedload
from sqlmodel import and_, or_, select, text, bindparam

from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest
from app.core.db import async_session
from typing import Type
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, select

from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest


class SearchProfileRepository:
    from sqlalchemy import and_, or_

    @staticmethod
    async def get_by_id(
        search_profile_id: UUID, current_user
    ) -> SearchProfile | None:
        user_id = current_user["id"]
        organization_id = current_user.get("organization_id")

        async with async_session() as session:
            stmt = select(SearchProfile).options(
                selectinload(SearchProfile.users)
            )

            # Basic filter: match the search profile by ID
            base_condition = SearchProfile.id == search_profile_id

            # Access conditions:
            # - public profile
            # - assigned to the user
            # - (optional) same organization
            access_conditions = [
                SearchProfile.is_public,
                SearchProfile.users.any(id=user_id),
            ]

            # Only include organization condition if the user has one
            if organization_id is not None:
                access_conditions.append(
                    SearchProfile.organization_id == organization_id
                )

            # Combine ID and access filters
            stmt = stmt.where(and_(base_condition, or_(*access_conditions)))

            result = await session.execute(stmt)
            return result.one_or_none()

    @staticmethod
    async def get_accessible_profiles(
        user_id: UUID, organization_id: UUID | None
    ) -> list[SearchProfile]:
        async with async_session() as session:
            stmt = select(SearchProfile).options(
                selectinload(SearchProfile.users)
            )

            if organization_id is not None:
                stmt = stmt.where(
                    (
                        (SearchProfile.is_public.is_(True))
                        & (SearchProfile.organization_id == organization_id)
                    )
                    | (SearchProfile.users.any(id=user_id))
                )
            else:
                stmt = stmt.where(SearchProfile.users.any(id=user_id))

            result = await session.execute(stmt.options(joinedload(SearchProfile.topics)))
            return result.unique().scalars().all()

    @staticmethod
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
