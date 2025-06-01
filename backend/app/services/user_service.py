from clerk_backend_api import Clerk
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_session

from app.core.config import configs
from app.models import User
from app.services.auth_service import UserCreate


class UserService:
    @staticmethod
    async def list_users() -> dict:
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

    @staticmethod
    async def create_user_if_not_exists(user_in: UserCreate) -> User:
        async with async_session() as session:
            query = select(User).where(User.id == user_in.clerk_id)
            result = await session.exec(query)
            existing_user = result.first()
            if existing_user:
                return existing_user

            user = User(**user_in.model_dump())
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

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
