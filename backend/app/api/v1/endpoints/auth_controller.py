
from fastapi import APIRouter

from app.services.auth_service import AuthService, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(user_data: UserCreate):
    return await AuthService.create_user(user_data)