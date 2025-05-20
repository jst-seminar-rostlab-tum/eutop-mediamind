import logging
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
        logging.error(f"Error fetching users: {e}")
        if "unauthorized" in error_msg or "invalid token" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
            )
        elif (
            "clerk" in error_msg
            or "connection" in error_msg
            or "unavailable" in error_msg
            or "timeout" in error_msg
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Clerk service is temporarily unavailable. "
                    "Please try again later."
                ),
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
    try:
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

    except Exception as e:
        logging.error(f"Error fetching current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch current user info: {str(e)}",
        )
