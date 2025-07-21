from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SearchProfile
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.topics_repository import TopicsRepository


def update_base_fields(
    profile: SearchProfile,
    name: str,
    is_public: bool,
    language: str,
    owner_id: UUID,
    current_user_id: UUID,
    is_superuser: bool,
):
    profile.name = name
    profile.is_public = is_public
    profile.language = language
    if current_user_id == profile.created_by_id or is_superuser:
        profile.owner_id = owner_id


async def update_topics(
    profile: SearchProfile,
    topics: List,
    session: AsyncSession,
):
    await TopicsRepository.update_topics(
        profile=profile,
        new_topics=topics,
        session=session,
    )


async def update_subscriptions(
    profile_id: UUID,
    subscriptions: List,
    session: AsyncSession,
):
    await SubscriptionRepository.set_subscriptions_for_profile(
        profile_id=profile_id,
        subscriptions=subscriptions,
        session=session,
    )


def update_emails(
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


def update_user_rights(
    profile: SearchProfile,
    can_read_user_ids: Optional[List[UUID]],
    can_edit_user_ids: Optional[List[UUID]],
):
    profile.can_read_user_ids = (
        [str(uid) for uid in can_read_user_ids] if can_read_user_ids else []
    )
    profile.can_edit_user_ids = (
        [str(uid) for uid in can_edit_user_ids] if can_edit_user_ids else []
    )
