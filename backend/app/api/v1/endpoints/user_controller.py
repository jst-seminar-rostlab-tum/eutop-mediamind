from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(_: Depends = Depends(get_current_user)):
    return await UserService.list_users()


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    return UserService.get_current_user_info(current_user)
