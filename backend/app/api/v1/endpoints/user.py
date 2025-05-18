from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=str)
def get_user_list():
    return "hello world"


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
