from typing import List
from uuid import UUID

from app.core.db import async_session
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription_schemas import (
    SetSearchProfileSubscriptionsRequest,
    SubscriptionSummary,
)


async def get_all_subscriptions_for_profile(
    search_profile_id: UUID,
) -> List[SubscriptionSummary]:
    async with async_session():
        return await SubscriptionRepository.get_all_subscriptions_with_search_profile(  # noqa: E501
            search_profile_id
        )


async def set_search_profile_subscriptions(
    request: SetSearchProfileSubscriptionsRequest,
) -> None:
    async with async_session() as session:
        await SubscriptionRepository.set_subscriptions_for_profile(
            profile_id=request.search_profile_id,
            subscriptions=request.subscriptions,
            session=session,
        )
