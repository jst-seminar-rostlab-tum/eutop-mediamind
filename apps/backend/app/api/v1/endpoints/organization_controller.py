import uuid
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user
from app.core.logger import get_logger
from app.models.user import UserRole
from app.schemas.organization_schemas import (
    OrganizationCreateOrUpdate,
    OrganizationResponse,
)
from app.schemas.request_response import FeedbackResponse
from app.schemas.subscription_schemas import (
    SetOrganizationSubscriptionsRequest,
    SubscriptionSummary,
)
from app.schemas.user_schema import UserEntity
from app.services.organization_service import OrganizationService

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    dependencies=[Depends(get_authenticated_user)],
)

logger = get_logger(__name__)


@router.post("", response_model=OrganizationResponse)
async def create_organization_with_users(
    organization_with_users: OrganizationCreateOrUpdate,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    return await OrganizationService.create_with_users(
        organization_with_users, current_user
    )


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization_with_users(
    organization_id: uuid.UUID,
    update_request: OrganizationCreateOrUpdate,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    return await OrganizationService.update_with_users(
        organization_id, update_request, current_user
    )


@router.put(
    "/{organization_id}/subscriptions",
    response_model=List[SubscriptionSummary],
)
async def set_organization_subscriptions(
    organization_id: UUID,
    request: SetOrganizationSubscriptionsRequest,
    current_user: UserEntity = Depends(get_authenticated_user),
) -> List[SubscriptionSummary]:
    if not (
        current_user.is_superuser
        or (
            current_user.role == UserRole.maintainer.value
            and current_user.organization_id == organization_id
        )
    ):
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    updated_subscriptions = (
        await OrganizationService.set_subscriptions_from_summary(
            organization_id, request.subscriptions
        )
    )

    return updated_subscriptions


@router.get("", response_model=List[OrganizationResponse])
async def get_all_organizations_with_users(
    current_user: UserEntity = Depends(get_authenticated_user),
) -> List[OrganizationResponse]:
    return await OrganizationService.get_all_with_users(current_user)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization_with_users(
    organization_id: uuid.UUID,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    return await OrganizationService.get_with_users(
        organization_id, current_user
    )


@router.delete("/{organization_id}", response_model=FeedbackResponse)
async def delete_organization(
    organization_id: uuid.UUID,
    current_user: UserEntity = Depends(get_authenticated_user),
):
    await OrganizationService.delete_organization(
        organization_id, current_user
    )
    return FeedbackResponse(status="success")
