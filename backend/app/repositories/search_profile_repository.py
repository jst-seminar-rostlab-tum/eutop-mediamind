from typing import Type
from uuid import UUID

from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.search_profile import SearchProfile
from app.schemas.search_profile_schemas import SearchProfileUpdateRequest


class SearchProfileRepository:

    @staticmethod
    async def get_by_id(search_profile_id: UUID) -> SearchProfile | None:
        async with async_session() as session:
            result = await session.exec(
                select(SearchProfile)
                .options(selectinload(SearchProfile.users))
                .where(SearchProfile.id == search_profile_id)
            )
            return result.one_or_none()

    @staticmethod
    async def get_accessible_profiles(
        user_id: UUID, organization_id: UUID
    ) -> list[SearchProfile]:
        async with async_session() as session:
            result = await session.exec(
                select(SearchProfile)
                .options(selectinload(SearchProfile.users))
                .where(
                    # Public in organization only
                    (
                        (SearchProfile.is_public.is_(True)) &
                        (SearchProfile.organization_id == organization_id)
                    )

                    | (SearchProfile.users.any(id=user_id))
                )
            )
            return result.all()

    @staticmethod
    async def update_by_id(
        profile_id: UUID, data: SearchProfileUpdateRequest
    ) -> Type[SearchProfile] | None:
        async with async_session() as session:
            profile = await session.get(SearchProfile, profile_id)
            if not profile:
                return None

            profile.name = data.name
            profile.is_public = data.public

            # Optional: Topics, Subscriptions, Emails bearbeiten

            session.add(profile)
            await session.commit()
            await session.refresh(profile)

            return profile
