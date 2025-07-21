from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from app.core.db import async_session
from app.models import SearchProfile
from app.models.user import UserRole
from app.repositories.email_repository import EmailRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.search_profile.search_profile_repository import (
    SearchProfileRepository,
)
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.search_profile_schemas import (
    SearchProfileCreateRequest,
    SearchProfileDetailResponse,
    SearchProfileUpdateRequest,
)
from app.schemas.user_schema import UserEntity

from .utils import _build_profile_response


async def create_search_profile(
    data: SearchProfileCreateRequest,
    current_user: UserEntity,
) -> SearchProfileDetailResponse:
    """
    Create a new SearchProfile plus its topics,
    subscriptions, emails, and rights.
    """
    async with async_session() as session:
        async with session.begin():
            profile = SearchProfile(
                name=data.name,
                is_public=data.is_public,
                organization_id=current_user.organization_id,
                created_by_id=current_user.id,
                owner_id=data.owner_id,
                language=data.language,
            )
            session.add(profile)
            await session.flush()

            # sync topics, subscriptions, emails, rights
            await TopicsRepository.update_topics(
                profile=profile,
                new_topics=data.topics,
                session=session,
            )
            await SubscriptionRepository.set_subscriptions_for_profile(
                profile_id=profile.id,
                subscriptions=data.subscriptions,
                session=session,
            )
            await EmailRepository.update_emails(
                profile_id=profile.id,
                organization_emails=data.organization_emails or [],
                profile_emails=data.profile_emails or [],
                session=session,
            )
            await SearchProfileRepository.update_user_rights(
                profile=profile,
                can_read_user_ids=data.can_read_user_ids,
                can_edit_user_ids=data.can_edit_user_ids,
                session=session,
            )

        # reload full profile with eager loading
        result = await session.execute(
            select(SearchProfile)
            .where(SearchProfile.id == profile.id)
            .options(*SearchProfileRepository._base_load_options())
        )
        fresh = result.scalar_one()

    return await _build_profile_response(fresh, current_user)


async def get_extended_by_id(
    search_profile_id: UUID,
    current_user: UserEntity,
) -> Optional[SearchProfileDetailResponse]:
    async with async_session():
        profile = await SearchProfileRepository.get_accessible_profile_by_id(
            search_profile_id=search_profile_id,
            user_id=current_user.id,
            user_role=current_user.role,
            is_superuser=current_user.is_superuser,
            organization_id=current_user.organization_id,
            session=async_session(),  # repo expects session
        )
    if not profile:
        return None
    return await _build_profile_response(profile, current_user)


async def get_available_search_profiles(
    current_user: UserEntity,
) -> List[SearchProfileDetailResponse]:
    async with async_session():
        profiles = await SearchProfileRepository.get_accessible_profiles(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            role=current_user.role,
            is_superuser=current_user.is_superuser,
        )
    return [await _build_profile_response(p, current_user) for p in profiles]


async def update_search_profile(
    search_profile_id: UUID,
    update_data: SearchProfileUpdateRequest,
    current_user: UserEntity,
) -> SearchProfileDetailResponse:
    async with async_session() as session:
        db_profile = (
            await SearchProfileRepository.get_accessible_profile_by_id(
                search_profile_id=search_profile_id,
                user_id=current_user.id,
                user_role=current_user.role,
                is_superuser=current_user.is_superuser,
                organization_id=current_user.organization_id,
                session=session,
            )
        )
        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # check edit rights
        allow_edit = (
            current_user.is_superuser
            or db_profile.created_by_id == current_user.id
            or (
                db_profile.organization_id == current_user.organization_id
                and current_user.role == UserRole.maintainer
            )
            or (
                db_profile.is_public
                and db_profile.organization_id == current_user.organization_id
            )
        )
        if not allow_edit:
            raise HTTPException(
                status_code=403, detail="Not allowed to edit this profile"
            )

        updated = await SearchProfileRepository.update_profile(
            profile=db_profile,
            data=update_data,
            current_user=current_user,
            session=session,
        )

    return await _build_profile_response(updated, current_user)


async def delete_search_profile(
    profile_id: UUID,
    current_user: UserEntity,
) -> None:
    # validate rights first
    profile = await SearchProfileRepository.get_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Search profile not found")
    allow_delete = (
        current_user.id == profile.owner_id
        or current_user.is_superuser
        or (
            current_user.role == UserRole.maintainer
            and current_user.organization_id == profile.organization_id
        )
    )
    if not allow_delete:
        raise HTTPException(
            status_code=403, detail="Not allowed to delete this profile"
        )

    async with async_session() as session:
        async with session.begin():
            # delete dependent records
            await MatchRepository.delete_for_search_profile(
                session, profile_id
            )
            await ReportRepository.delete_for_search_profile(
                session, profile_id
            )
            await SubscriptionRepository.delete_links_for_search_profile(
                session, profile_id
            )
            await UserRepository.delete_links_for_search_profile(
                session, profile_id
            )
            topic_ids = [t.id for t in profile.topics]
            await TopicsRepository.delete_keyword_links_for_search_profile(
                session, topic_ids
            )
            await TopicsRepository.delete_for_search_profile(
                session, profile_id
            )
            await SearchProfileRepository.delete_by_id(session, profile_id)
