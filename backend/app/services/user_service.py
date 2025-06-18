from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import engine
from app.models import User
from app.repositories.user_repository import (
    get_user_by_clerk_id,
    get_user_list_from_organization,
    update_language,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class UserService:
    @staticmethod
    async def list_users(user: User) -> list[User] | User:
        return await get_user_list_from_organization(user)

    @staticmethod
    def get_current_user_info(current_user: User) -> User:
        return current_user

    @staticmethod
    async def update_user_language(language, user):
        # 1) fetch
        user = await get_user_by_clerk_id(user.clerk_id)

        # 2) update
        return await update_language(user, language)
