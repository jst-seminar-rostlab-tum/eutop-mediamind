# app/services/user_service.py

from typing import Optional

from clerk_backend_api import Clerk
from pydantic import BaseModel

from app.core.config import configs


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserService:
    @staticmethod
    async def list_users() -> list[dict]:
        async with Clerk(bearer_auth=configs.CLERK_SECRET_KEY) as clerk:
            users = await clerk.users.list_async()
            return [
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

    @staticmethod
    def get_current_user_info(current_user: dict) -> dict:
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
