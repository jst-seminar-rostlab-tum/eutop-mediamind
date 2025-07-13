from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_authenticated_user, get_sync_user
from app.core.languages import Language
from app.core.logger import get_logger
from app.models.user import Gender, User
from app.schemas.request_response import FeedbackResponse
from app.schemas.user_schema import UserEntity
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

logger = get_logger(__name__)


@router.get("", response_model=Union[List[UserEntity], UserEntity])
async def get_users(
    current_user: UserEntity = Depends(get_authenticated_user),
) -> List[UserEntity]:
    """
    List all users visible (same organization) to the current user or
    return the single user if restricted.
    """
    try:
        return await UserService.get_all_by_organization(current_user)
    except Exception as e:
        logger.error(
            "Error listing users for user with id=%s: %s", current_user.id, e
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to list users",
        )


@router.get("/all", response_model=Union[List[UserEntity], UserEntity])
async def get_all_users(
    current_user: UserEntity = Depends(get_authenticated_user),
) -> List[UserEntity]:
    """
    List all users visible to the current user or
    return the single user if restricted.
    """
    try:
        return await UserService.get_all(current_user)
    except Exception as e:
        logger.error(
            "Error listing users for user with id=%s: %s", current_user.id, e
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to list users",
        )


@router.get("/me", response_model=UserEntity)
async def get_current_user_info(
    current_user: UserEntity = Depends(get_authenticated_user),
) -> UserEntity:
    """
    Retrieve the authenticated user's profile information.
    """
    return current_user


@router.post("/sync", response_model=UserEntity)
async def sync_user(
    synced_user: UserEntity = Depends(get_sync_user),
) -> UserEntity:
    """
    Synchronize the current user with the external Clerk service.
    """
    return synced_user


@router.put("/language", response_model=UserEntity)
async def update_language(
    language: Language = Query(...), user=Depends(get_sync_user)
):
    return await UserService.update_user_language(language, user)


@router.put("/gender", response_model=UserEntity)
async def update_gender(
    gender: Gender = Query(...),
    user=Depends(get_sync_user),
):
    return await UserService.update_gender(gender, user)


@router.put("/breaking_news", response_model=UserEntity)
async def update_breaking_news(
    user=Depends(get_sync_user),
    breaking_news: bool = Query(...),
):
    return await UserService.update_breaking_news(breaking_news, user)


@router.delete("", response_model=FeedbackResponse)
async def delete_current_user(
    current_user: User = Depends(get_authenticated_user),
):
    """
    Delete the authenticated user's account.
    """
    logger.warning(
        "Deletion attempted for user %s, but endpoint not implemented.",
        current_user.id,
    )
    raise HTTPException(
        status_code=403,
        detail="Not implemented yet",
    )
