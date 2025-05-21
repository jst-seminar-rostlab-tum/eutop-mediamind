from clerk_backend_api import Clerk
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import configs

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    email_address: str
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


@router.post("/signup")
async def signup(user_data: UserCreate):
    try:
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            user = await clerk.users.create_async(
                request={
                    "email_address": [user_data.email_address],
                    "password": user_data.password,
                    "username": user_data.username,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "skip_password_checks": True,
                    "skip_password_requirement": False,
                }
            )

            return {
                "id": user.id,
                "email": (
                    user.email_addresses[0].email_address
                    if user.email_addresses
                    else None
                ),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )
