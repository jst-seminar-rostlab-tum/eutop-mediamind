from fastapi import APIRouter, HTTPException, status
from app.services.auth_service import AuthService, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(user_data: UserCreate):
    try:
        user = await AuthService.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )
