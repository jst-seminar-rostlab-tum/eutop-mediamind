from typing import Optional

from clerk_backend_api import Clerk
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import configs
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.get("")
async def list_users(_: Depends = Depends(get_current_user)):
    try:
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            users = await clerk.users.list_async()
            return {
                "users": [
                    {
                        "id": user.id,
                        "email": (
                            user.email_addresses[0].email_address
                            if user.email_addresses
                            else None
                        ),
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }
                    for user in users
                ]
            }

    except Exception as e:
        error_msg = str(e).lower()
        if "unauthorized" in error_msg or "invalid token" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}",
        )


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information from Clerk
    """
    return {
        "id": current_user["id"],
        "email": (
            current_user["email_addresses"][0]["email_address"]
            if current_user.get("email_addresses")
            else None
        ),
        "first_name": current_user.get("first_name"),
        "last_name": current_user.get("last_name"),
    }
