from clerk_backend_api import Clerk
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import configs
from app.core.dependencies import get_current_user

router = APIRouter()

# init Clerk client
clerk = Clerk(bearer_auth=configs.CLERK_SECRET_KEY)


class UserCreate(BaseModel):
    email_address: str
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user.get("email_addresses", [{}])[0].get(
            "email_address"
        ),
        "first_name": current_user.get("first_name"),
        "last_name": current_user.get("last_name"),
    }


@router.get("/users")
async def list_users(_: Depends = Depends(get_current_user)):
    try:
        users = clerk.users.list()
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}",
        )


@router.post("/signup")
async def signup(user_data: UserCreate):
    """
    Sign up a new user
    """
    try:
        with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            user = clerk.users.create(
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
