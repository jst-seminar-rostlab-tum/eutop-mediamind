import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import configs
from app.core.dependencies import get_current_user

router = APIRouter()


class UserCreate(BaseModel):
    email_address: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information
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


@router.get("/users")
async def list_users(current_user=Depends(get_current_user)):
    """
    List all users (requires authentication)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.clerk.dev/v1/users",
            headers={
                "Authorization": f"Bearer {configs.CLERK_SECRET_KEY}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch users from Clerk",
            )

        users_data = response.json()
        return {
            "users": [
                {
                    "id": user["id"],
                    "email": (
                        user["email_addresses"][0]["email_address"]
                        if user.get("email_addresses")
                        else None
                    ),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                }
                for user in users_data
            ]
        }


@router.post("/users")
async def create_user(user_data: UserCreate):
    """
    Create a new user
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.clerk.dev/v1/users",
            headers={
                "Authorization": f"Bearer {configs.CLERK_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "email_address": user_data.email_address,
                "password": user_data.password,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in Clerk",
            )

        user = response.json()
        return {
            "id": user["id"],
            "email": (
                user["email_addresses"][0]["email_address"]
                if user.get("email_addresses")
                else None
            ),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
        }
