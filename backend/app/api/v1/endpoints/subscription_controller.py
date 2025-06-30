from fastapi import APIRouter, Depends

from app.core.auth import get_authenticated_user
from app.schemas.subscription_schemas import SubscriptionSummary
from app.services.subscription_service import SubscriptionService

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
