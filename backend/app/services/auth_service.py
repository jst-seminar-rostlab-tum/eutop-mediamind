# app/services/auth_service.py

from clerk_backend_api import Clerk
from app.core.config import configs
from pydantic import BaseModel


class UserCreate(BaseModel):
    email_address: str
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


class AuthService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> dict:
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
