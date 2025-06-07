from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.schemas.subscription_schemas import (
    SetSearchProfileSubscriptionsRequest,
    SubscriptionSummary,
)
from app.services.llm_service.subscription_service import SubscriptionService
from app.services.search_profiles_service import SearchProfileService

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)

@router.get(
    "",
    response_model=list[SubscriptionSummary],
)
async def get_all_subscriptions():
    return await SubscriptionService.get_all_subscriptions()

@router.get(
    "/{search_profile_id}",
    response_model=list[SubscriptionSummary],
)
async def get_all_subscriptions_with_search_profile(search_profile_id: UUID):
    return await SearchProfileService.get_all_subscriptions_for_profile(
        search_profile_id
    )


@router.post("")
async def set_subscriptions_for_search_profile(
    request: SetSearchProfileSubscriptionsRequest,
):
    await SearchProfileService.set_search_profile_subscriptions(request)
    return {"detail": "Subscriptions updated successfully"}
