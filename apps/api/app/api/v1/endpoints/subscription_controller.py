from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.schemas.subscription_schemas import (
    SubscriptionCreateOrUpdate,
    SubscriptionRead,
    SubscriptionSummary,
)
from app.schemas.user_schema import UserEntity
from app.services.subscription_service import SubscriptionService

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)


def _assert_admin(user: UserEntity):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")


@router.get(
    "",
    response_model=List[SubscriptionSummary],
)
async def get_all_subscriptions(
    current_user: UserEntity = Depends(get_authenticated_user),
):
    _assert_admin(current_user)
    return await SubscriptionService.get_all_subscriptions()


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionRead,
)
async def get_subscription(
    subscription_id: UUID,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    _assert_admin(current_user)
    return await SubscriptionService.get(subscription_id)


@router.post("", response_model=SubscriptionRead)
async def create_subscription(
    data: SubscriptionCreateOrUpdate,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    _assert_admin(current_user)
    return await SubscriptionService.create(data)


@router.put("/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription(
    subscription_id: UUID,
    data: SubscriptionCreateOrUpdate,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    _assert_admin(current_user)
    return await SubscriptionService.update(subscription_id, data)


@router.delete("/{subscription_id}", response_model=dict)
async def delete_subscription(
    subscription_id: UUID,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    _assert_admin(current_user)
    await SubscriptionService.delete(subscription_id)
    return {"status": "deleted"}
