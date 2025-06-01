from clerk_backend_api import Clerk
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import configs
from app.core.db import engine
from app.models import User
from app.models.user import UserCreate

async_session = async_sessionmaker(engine, expire_on_commit=False)


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
            query = select(User).where(User.clerk_id == user_in.clerk_id)
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # Check if any fields have changed
                updated = False
                if existing_user.email != user_in.email:
                    existing_user.email = user_in.email
                    updated = True
                if existing_user.first_name != user_in.first_name:
                    existing_user.first_name = user_in.first_name
                    updated = True
                if existing_user.last_name != user_in.last_name:
                    existing_user.last_name = user_in.last_name
                    updated = True

                if updated:
                    session.add(existing_user)
                    await session.commit()
                    await session.refresh(existing_user)

                return existing_user

            # Create new user if not found
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
