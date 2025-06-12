from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_authenticated_user, get_sync_user
from app.core.logger import get_logger
from app.models.user import User
from app.schemas.request_response import FeedbackResponse
from app.schemas.user_schema import UserEntity
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

logger = get_logger(__name__)


@router.get("", response_model=list[User] | User)
async def list_users(current_user=Depends(get_authenticated_user)):
    return await UserService.list_users(current_user)


@router.get("/me", response_model=UserEntity)
async def get_current_user_info(current_user=Depends(get_authenticated_user)):
    return current_user


@router.post("/sync", response_model=UserEntity)
async def sync_user_with_clerk(user=Depends(get_sync_user)):
    return user


@router.delete("/me", response_model=FeedbackResponse)
async def delete_current_user(current_user=Depends(get_authenticated_user)):
    raise HTTPException(status_code=403, detail="Not Implemented jet")
